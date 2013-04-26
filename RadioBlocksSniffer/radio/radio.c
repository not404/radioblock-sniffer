/* Copyright (c) 2011  Colorado Micro Devices Corporation
   All rights reserved.

   Redistribution and use in source and binary forms, with or without
   modification, are permitted provided that the following conditions are met:

   * Redistributions of source code must retain the above copyright
     notice, this list of conditions and the following disclaimer.
   * Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in
     the documentation and/or other materials provided with the
     distribution.
   * Neither the name of the copyright holders nor the names of
     contributors may be used to endorse or promote products derived
     from this software without specific prior written permission.

  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
  ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
  LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
  CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
  SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
  INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
  CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
  POSSIBILITY OF SUCH DAMAGE.
*/
/*
  $Id: radio.c,v 1.1 2012/04/25 17:42:57 cvsuser Exp $
*/

/*============================ INCLUDE =======================================*/

#include "radio.h"
#include "hal.h"
#include "rf231.h"
#include "timer16.h"
#include <stdbool.h>
#include <stdlib.h>

#define true 1
#define false 0

/*
   The radio interface is a driver for the Atmel 802.15.4 radio chips.
   This code works with the AT86RF231.

   This driver code is fairly modular, and can be modified to be used
   without the RUM MAC layer that lies on top.

   The radio interface involves an SPI port and several digital I/O
   lines.  See the radio chip datasheet for details.
*/


/*============================ TYPEDEFS ======================================*/

/*  This enumeration defines the necessary timing information for the
    AT86RF231 radio transceiver. All times are in microseconds.

    These constants are extracted from the datasheet (actually from the RF230 
    datasheet).
*/
typedef enum{
    TIME_TO_ENTER_P_ON               = 510, // Transition time from VCC is applied to P_ON.
    TIME_P_ON_TO_TRX_OFF             = 510, // Transition time from P_ON to TRX_OFF.
    TIME_SLEEP_TO_TRX_OFF            = 880, // Transition time from SLEEP to TRX_OFF.
    TIME_RESET                       = 6,   // Time to hold the RST pin low during reset
    TIME_ED_MEASUREMENT              = 140, // Time it takes to do a ED measurement.
    TIME_CCA                         = 140, // Time it takes to do a CCA.
    TIME_PLL_LOCK                    = 150, // Maximum time it should take for the PLL to lock.
    TIME_FTN_TUNING                  = 25,  // Maximum time it should take to do the filter tuning.
    TIME_NOCLK_TO_WAKE               = 6,   // Transition time from *_NOCLK to being awake.
    TIME_CMD_FORCE_TRX_OFF           = 1,   // Time it takes to execute the FORCE_TRX_OFF command.
    TIME_TRX_OFF_TO_PLL_ACTIVE       = 180, // Transition time from TRX_OFF to: RX_ON, PLL_ON, TX_ARET_ON and RX_AACK_ON.
    TIME_STATE_TRANSITION_PLL_ACTIVE = 1,   // Transition time from PLL active state to another.
    TIME_RESET_TRX_OFF               = 37,  // Transition time from RESET to TRX_OFF
}radio_trx_timing_t;
/*============================ VARIABLES =====================================*/
u8 rx_mode;         // Flag: are we in RX mode?
_Bool frame_received = 0;

u16 remote_node_address = 0;
u8 seq = 0; 
u16 panid = 0;
u16 short_address = 0;

static u8 rssi_val;

/*============================ PROTOTYPES ====================================*/
void radioRxStartEvent(u8 const frame_length);
void radioTrxend_event(void);


/* 
   Initialize the radio chip.

   If the initialization is successful the radio transceiver will be
   in TRX_OFF state.

   @note This function must be called prior to any of the other
   functions in this file! Can be called from any transceiver state.

   There is a parameter (SR_CCA_ED_THRES) that sets the energy
   threshold for determining if a channel is clear before the radio
   can send a packet.  If the threshold is set too low, then in the
   presence of interference the radio may never get a chance to send a
   packet, and will be cut off from the network.  If the threshold is
   set too high, then each node may "yell over" the other nodes and
   disrupt other network connections.  The default value is 7, and a
   value of 2 was useful for testing the initial 2.4GHz version of the
   network.  Interference caused problems in the 900MHz band, and the
   threshold was raised back up to 7.  This parameter may be
   auto-tuned by application software in the future.

   @param cal_rc_osc If true, the radio's accurate clock is used to
   calibrate the CPU's internal RC oscillator.

   @retval RADIO_SUCCESS The radio transceiver was successfully
   initialized and put into the TRX_OFF state.

   @retval RADIO_UNSUPPORTED_DEVICE The connected device is not an
   Atmel AT86RF230 radio transceiver.

   @retval RADIO_TIMED_OUT The radio transceiver was not able to
   initialize and enter TRX_OFF state within the specified time.
*/

radio_status_t radio_init(void)
{
    radio_status_t init_status = RADIO_SUCCESS;

    delay_microseconds(0, TIME_TO_ENTER_P_ON);

    //Initialize Hardware Abstraction Layer.
    hal_init();

    radio_reset_trx(); //Do HW reset of radio transceiver.


    //Force transition to TRX_OFF.
    hal_subregister_write(SR_TRX_CMD, CMD_FORCE_TRX_OFF);

    delay_microseconds(0, TIME_P_ON_TO_TRX_OFF); //Wait for the transition to be complete.

#if !SNIFFER_MODE
    hal_register_write(RG_IRQ_MASK, RF2xx_SUPPORTED_INTERRUPT_MASK);

    // Set the CCA ED threshold really low
    //hal_subregister_write(SR_CCA_ED_THRES, 7);

    // Use automatic CRC/FCS.
    radio_use_auto_tx_crc();

    // Turn on for receiving
    radio_set_trx_state(RX_ON);
#endif // !SNIFFER_MODE

#if SNIFFER_MODE
    // Configure radio for sniffer mode.

    hal_register_write(RG_SHORT_ADDR_0, 0);
    hal_register_write(RG_SHORT_ADDR_1, 0);

    hal_register_write(RG_PAN_ID_0, 0);
    hal_register_write(RG_PAN_ID_1, 0);

    hal_register_write(RG_IEEE_ADDR_0, 0);
    hal_register_write(RG_IEEE_ADDR_1, 0);
    hal_register_write(RG_IEEE_ADDR_2, 0);
    hal_register_write(RG_IEEE_ADDR_3, 0);
    hal_register_write(RG_IEEE_ADDR_4, 0);
    hal_register_write(RG_IEEE_ADDR_5, 0);
    hal_register_write(RG_IEEE_ADDR_6, 0);
    hal_register_write(RG_IEEE_ADDR_7, 0);

    // Turn on the promiscuous bit.
    hal_subregister_write(SR_AACK_PROM_MODE, 1);

    // Disable ACKs in promiscuous mode.
    hal_register_write(RG_CSMA_SEED_1, 0x10);
#endif // SNIFFER_MODE

    // Only generate TRX End interrupts.
    hal_register_write(RG_IRQ_MASK, RF2xx_SUPPORTED_INTERRUPT_MASK);

#if !SNIFFER_MODE
    //Force transition to TRX_OFF.
    hal_subregister_write(SR_TRX_CMD, CMD_FORCE_TRX_OFF);

    delay_microseconds(0, TIME_P_ON_TO_TRX_OFF); //Wait for the transition to be complete.

    // Put radio into PLL_ON before transition to RX_AACK mode
 	radio_set_trx_state(PLL_ON);

    delay_microseconds(0, TIME_TRX_OFF_TO_PLL_ACTIVE); //Wait for the transition to be complete.
#endif // SNIFFER_MODE
    // Put radio into RX_AACK mode
    hal_subregister_write(SR_TRX_CMD, RX_ON);

    return init_status;
}

/* 
   Returns the radio part number.  The value returned is shown
   in the radio datasheet.  This value is valid any time after
   radioInit() is called.

   @return RF230
   @return RF231
   @return RF212
*/
u8 radio_get_part_num(void)
{
    static u8 radio_part_number;

    if (!radio_part_number)
        radio_part_number = hal_register_read(RG_PART_NUM);
    return radio_part_number;
}


/* 
   Retrieves the saved RSSI (Received Signal Strength
   Indication) value.  The value returned is the RSSI at the time of
   the RX_START interrupt.

   @return The RSSI value, which ranges from 0 to 28, and can be used
   to calculate the RSSI in dBm:

   Input Signal Strength (in dBm) = -90dBm + (3 * RSSI - 1)
*/
u8 radio_get_saved_rssi_value(void)
{
    if (radio_get_part_num() != RF231)
        // No RX_START interrupt, therefore no RSSI reading
        return 22;
    return rssi_val;
}

/* 
   Retrieves the saved LQI (Link Quality Indication) value.
   The value returned is the LQI for the last packet received.

   @return The LQI value, which ranges from 0 to 255.
*/
u8 radio_get_saved_lqi_value(void)
{
    return ((rx_frame_t*)trx_buf)->lqi;
}

/* 
   Callback function, called when the radio has received a
   TRX_END interrupt.
*/
void radio_trx_end_event(void)
{
    //if (rx_mode)
    volatile u8 state = radio_get_trx_state();
    if((state == BUSY_RX_AACK) || (state == RX_ON) || (state == BUSY_RX) || (state == RX_AACK_ON))
    {
      hal_frame_read();
    }
    else if ((state == BUSY_TX) || (state == BUSY_TX_ARET) || (state == TX_ARET_ON) || (state == PLL_ON))
    {
        // Put radio back into receive mode.
        radio_set_trx_state(RX_AACK_ON);
    }
}


/*  
    This function will return the channel used by the radio transceiver.
 
    @return Current channel, 11 to 26.
 */
u8 radio_get_channel(void)
{
	u8 chann;

    // Only the lowest 5 bits have channel information, therefore, mask off
    // bits that have no channel info.
	//chann = 0x1F && hal_subregister_read(SR_CHANNEL);
	chann = hal_subregister_read(SR_CHANNEL);
    return (chann);
}

/*  
    This function will change the operating channel.
  
    @param  channel New channel to operate on. Must be between 11 and 26.
  
    @retval RADIO_SUCCESS New channel set.
    @retval RADIO_WRONG_STATE Transceiver is in a state where the channel cannot
                              be changed (SLEEP).
    @retval RADIO_INVALID_ARGUMENT Channel argument is out of bounds.
    @retval RADIO_TIMED_OUT The PLL did not lock within the specified time.
 */
radio_status_t radio_set_channel(u8 channel)
{
    /*Do function parameter and state check.*/

    if (((int8_t)channel < MIN_CHANNEL && MIN_CHANNEL) ||
        (channel > MAX_CHANNEL))
        return RADIO_INVALID_ARGUMENT;

    if (radio_get_channel() == channel)
        return RADIO_SUCCESS;

    /*Set new operating channel.*/
    hal_subregister_write(SR_CHANNEL, channel);

    //Read current state and wait for the PLL_LOCK interrupt if the
    //radio transceiver is in either RX_ON or PLL_ON.
    u8 trx_state = radio_get_trx_state();

    if ((trx_state == RX_ON) ||
        (trx_state == PLL_ON))
    	delay_microseconds(0, TIME_PLL_LOCK);

    radio_status_t channel_set_status = RADIO_TIMED_OUT;

    //Check that the channel was set properly.
    if (radio_get_channel() == channel)
        channel_set_status = RADIO_SUCCESS;

    return channel_set_status;
}


/*  
    This function will change the output power level.
  
    @param  power_level New output power level in the "TX power settings"
                        as defined in the radio transceiver's datasheet.
  
    @retval RADIO_SUCCESS New output power set successfully.
    @retval RADIO_INVALID_ARGUMENT The supplied function argument is out of bounds.
    @retval RADIO_WRONG_STATE It is not possible to change the TX power when the
                            device is sleeping.
 */
radio_status_t radio_set_tx_power_level(u8 power_level)
{

    /*Check function parameter and state.*/
    if (power_level > TX_PWR_17_2DBM)
        return RADIO_INVALID_ARGUMENT;

    /*Set new power level*/
    hal_subregister_write(SR_TX_PWR, power_level);

    return RADIO_SUCCESS;
}


/*  
    This function returns the Received Signal Strength Indication.
  
    This function should only be called from the: RX_ON and BUSY_RX. This
    can be ensured by reading the current state of the radio transceiver
    before executing this function!
  
    @param rssi Pointer to memory location where RSSI value should be written.
    @retval RADIO_SUCCESS The RSSI measurement was successful.
    @retval RADIO_WRONG_STATE The radio transceiver is not in RX_ON or BUSY_RX.
 */
radio_status_t radio_get_rssi_value(u8 *rssi)
{

    u8 current_state = radio_get_trx_state();
    radio_status_t retval = RADIO_WRONG_STATE;

    /*The RSSI measurement should only be done in RX_ON or BUSY_RX.*/
    if ((current_state == RX_ON) ||
        (current_state == BUSY_RX))
    {
        *rssi = hal_subregister_read(SR_RSSI);
        retval = RADIO_SUCCESS;
    }

    return retval;
}

/*  
    This function changes the prescaler on the CLKM pin.
  
    @param direct   This boolean variable is used to determine if the frequency
                    of the CLKM pin shall be changed directly or not. If direct
                    equals true, the frequency will be changed directly. This is
                    fine if the CLKM signal is used to drive a timer etc. on the
                    connected microcontroller. However, the CLKM signal can also
                    be used to clock the microcontroller itself. In this situation
                    it is possible to change the CLKM frequency indirectly
                    (direct == false). When the direct argument equlas false, the
                    CLKM frequency will be changed first after the radio transceiver
                    has been taken to SLEEP and awaken again.
    @param clock_speed This parameter can be one of the following constants:
                       CLKM_DISABLED, CLKM_1MHZ, CLKM_2MHZ, CLKM_4MHZ, CLKM_8MHZ
                       or CLKM_16MHZ.
  
    @retval RADIO_SUCCESS Clock speed updated. New state is TRX_OFF.
    @retval RADIO_INVALID_ARGUMENT Requested clock speed is out of bounds.s
 */
radio_status_t radio_set_clock_speed(_Bool direct, u8 clock_speed)
{
    /*Check function parameter and current clock speed.*/
    if (clock_speed > CLKM_16MHZ)
        return RADIO_INVALID_ARGUMENT;

    /*Select to change the CLKM frequency directly or after returning from SLEEP.*/
    if (direct == false)
        hal_subregister_write(SR_CLKM_SHA_SEL, 1);
    else
        hal_subregister_write(SR_CLKM_SHA_SEL, 0);

    hal_subregister_write(SR_CLKM_CTRL, clock_speed);
    return RADIO_SUCCESS;
}

/*  
    This function return the Radio Transceivers current state.
  
    @retval     P_ON               When the external supply voltage (VDD) is
                                   first supplied to the transceiver IC, the
                                   system is in the P_ON (Poweron) mode.
    @retval     BUSY_RX            The radio transceiver is busy receiving a
                                   frame.
    @retval     BUSY_TX            The radio transceiver is busy transmitting a
                                   frame.
    @retval     RX_ON              The RX_ON mode enables the analog and digital
                                   receiver blocks and the PLL frequency
                                   synthesizer.
    @retval     TRX_OFF            In this mode, the SPI module and crystal
                                   oscillator are active.
    @retval     PLL_ON             Entering the PLL_ON mode from TRX_OFF will
                                   first enable the analog voltage regulator. The
                                   transceiver is ready to transmit a frame.
    @retval     BUSY_RX_AACK       The radio was in RX_AACK_ON mode and received
                                   the Start of Frame Delimiter (SFD). State
                                   transition to BUSY_RX_AACK is done if the SFD
                                   is valid.
    @retval     BUSY_TX_ARET       The radio transceiver is busy handling the
                                   auto retry mechanism.
    @retval     RX_AACK_ON         The auto acknowledge mode of the radio is
                                   enabled and it is waiting for an incomming
                                   frame.
    @retval     TX_ARET_ON         The auto retry mechanism is enabled and the
                                   radio transceiver is waiting for the user to
                                   send the TX_START command.
    @retval     RX_ON_NOCLK        The radio transceiver is listening for
                                   incomming frames, but the CLKM is disabled so
                                   that the controller could be sleeping.
                                   However, this is only true if the controller
                                   is run from the clock output of the radio.
    @retval     RX_AACK_ON_NOCLK   Same as the RX_ON_NOCLK state, but with the
                                   auto acknowledge module turned on.
    @retval     BUSY_RX_AACK_NOCLK Same as BUSY_RX_AACK, but the controller
                                   could be sleeping since the CLKM pin is
                                   disabled.
    @retval     STATE_TRANSITION   The radio transceiver's state machine is in
                                   transition between two states.
 */
u8 radio_get_trx_state(void)
{
    return hal_subregister_read(SR_TRX_STATUS);
}


/*  
    This function will change the current state of the radio
           transceiver's internal state machine.
 
   @param     new_state      Here is a list of possible states:
              - RX_ON        Requested transition to RX_ON state.
              - TRX_OFF      Requested transition to TRX_OFF state.
              - PLL_ON       Requested transition to PLL_ON state.
              - RX_AACK_ON   Requested transition to RX_AACK_ON state.
              - TX_ARET_ON   Requested transition to TX_ARET_ON state.
 
   @retval    RADIO_SUCCESS           Requested state transition completed
                                      successfully.
   @retval    RADIO_INVALID_ARGUMENT  Supplied function parameter out of bounds.
   @retval    RADIO_WRONG_STATE       Illegal state to do transition from.
   @retval    RADIO_BUSY_STATE        The radio transceiver is busy.
   @retval    RADIO_TIMED_OUT         The state transition could not be completed
                                      within resonable time.
 */
radio_status_t radio_set_trx_state(u8 new_state)
{
    u8 original_state;

    /*Check function paramter and current state of the radio transceiver.*/
    if (!((new_state == TRX_OFF)    ||
          (new_state == RX_ON)      ||
          (new_state == PLL_ON)     ||
          (new_state == RX_AACK_ON) ||
          (new_state == TX_ARET_ON)))
        return RADIO_INVALID_ARGUMENT;

    // Wait for radio to finish previous operation
    while (radio_is_busy())
        ;

    original_state = radio_get_trx_state();
    if (new_state == original_state)
        return RADIO_SUCCESS;

    //At this point it is clear that the requested new_state is:
    //TRX_OFF, RX_ON, PLL_ON, RX_AACK_ON or TX_ARET_ON.

    //The radio transceiver can be in one of the following states:
    //TRX_OFF, RX_ON, PLL_ON, RX_AACK_ON, TX_ARET_ON.
    if(new_state == TRX_OFF)
        radio_reset_state_machine(); //Go to TRX_OFF from any state.
    else
    {
        //It is not allowed to go from RX_AACK_ON or TX_AACK_ON and directly to
        //TX_AACK_ON or RX_AACK_ON respectively. Need to go via RX_ON or PLL_ON.
        if ((new_state == TX_ARET_ON) &&
            (original_state != PLL_ON))
        {
            //First do intermediate state transition to PLL_ON, then to TX_ARET_ON.
            //The final state transition to TX_ARET_ON is handled after the if-else if.
            hal_subregister_write(SR_TRX_CMD, PLL_ON);
        }
        else if ((new_state == RX_AACK_ON) &&
                 (original_state != PLL_ON))
        {
            //First do intermediate state transition to PLL_ON, then to RX_AACK_ON.
            hal_subregister_write(SR_TRX_CMD, PLL_ON);
        }

        //Any other state transition can be done directly.
        hal_subregister_write(SR_TRX_CMD, new_state);

    } // end: if(new_state == TRX_OFF) ...

    /*Verify state transition.*/
    radio_status_t set_state_status = RADIO_TIMED_OUT;

    if (radio_get_trx_state() == new_state)
        set_state_status = RADIO_SUCCESS;

    return set_state_status;
}


/*  
    This function will reset the state machine (to TRX_OFF) from any of
    its states, except for the SLEEP state.
 */
void radio_reset_state_machine(void)
{
    hal_set_slptr_low();
    delay_microseconds(0, TIME_NOCLK_TO_WAKE);
    hal_subregister_write(SR_TRX_CMD, CMD_FORCE_TRX_OFF);
    delay_microseconds(0, TIME_CMD_FORCE_TRX_OFF);
}


/*  
    This function will reset all the registers and the state machine of
    the radio transceiver.
 */
void radio_reset_trx(void)
{
    hal_set_rst_low();
    hal_set_slptr_low();
    delay_microseconds(0, TIME_RESET);
    hal_set_rst_high();
}


/*  
    This function will enable or disable automatic CRC during frame
    transmission.
  
    @param  auto_crc_on If this parameter equals true auto CRC will be used for
                        all frames to be transmitted. The framelength must be
                        increased by two bytes (16 bit CRC). If the parameter equals
                        false, the automatic CRC will be disabled.
 */
void radio_use_auto_tx_crc(void)
{
	hal_subregister_write(SR_TX_AUTO_CRC_ON_231, 1);
}


/* 
   Check whether the radio chip is busy. This can be used to make sure
   the radio is free to send another packet.  If the radio is busy and
   the MAC is directed to send another packet, then radio_send_data()
   will simply wait for the radio to be free before proceeding.

   @return true  Radio is busy.
   @return false Radio is free to use.
*/
u8 radio_is_busy(void)
{
    u8 state;

    state = radio_get_trx_state();
    return (state == BUSY_RX_AACK ||
            state == BUSY_TX_ARET ||
            state == BUSY_TX ||
            state == BUSY_RX ||
            state == BUSY_RX_AACK_NOCLK);
}


/*  
    This function will download a frame to the radio
    transceiver's transmit buffer and send it.  If the radio
    is currently busy receiving or transmitting, this function
    will block processing waiting for the radio to finish its
    current operation.  You can avoid blocking by checking
    that radio_is_busy() return false before calling this
    function.
  
    @param  data_length Length of the frame to be transmitted. 1 to 128 bytes are the valid lengths.
            The data length is padded by two to account for the auto-CRC, which is used in every frame.
    @param  *data   Pointer to the data to transmit
  
    @retval RADIO_SUCCESS           Frame downloaded and sent successfully.
    @retval RADIO_INVALID_ARGUMENT  If the dataLength is 0 byte or more than 127
                                    bytes the frame will not be sent.
    @retval RADIO_WRONG_STATE       It is only possible to use this function in the
                                    PLL_ON and TX_ARET_ON state. If any other state is
                                    detected this error message will be returned.
 */
radio_status_t radio_send_data(u8 data_length, u8 *data)
{
#if MAC_LAYER  
    // Check we aren't in sniffer mode, hence never TX
    if ((macConfig.sniffMode == sniff_everything) || (macConfig.sniffMode == spectrum_analyzer))
    {
        return RADIO_WRONG_STATE;
    }
    // Check if we should record outgoing frames too
    else if (macConfig.sniffMode != sniff_none && DEBUG)
    {
        event_object_t event;
        
        if(macQueueAddFromMem(data, data_length, 0, &SnifferQueue))
        {
            event.event = MAC_EVENT_SNIFFY;
            event.data = (void (*)(void))SNIFFER_CIRCBUF;
            mac_put_event(&event);
        }
    }
#endif // MAC_LAYER    
    // Check function parameters and current state.
    if (data_length > RF2xx_MAX_TX_FRAME_LENGTH)
        return RADIO_INVALID_ARGUMENT;
    
    // Wait for radio to get unbusy
    while (radio_is_busy())
        ;

    // Put radio in PLL_ON state
    do
    {
        radio_set_trx_state(PLL_ON);
    } while (radio_get_trx_state() != PLL_ON);

    /*Do frame transmission.*/
    hal_frame_write(data, data_length+2); //Then write data to the frame buffer.

    return RADIO_SUCCESS;
}


/*  
    This function will set the I_AM_COORD sub register.
  
    @param[in] i_am_coordinator If this parameter is true, the associated
                                coordinator role will be enabled in the radio
                                transceiver's address filter.
                                False disables the same feature.
 */
void radio_set_device_role(_Bool i_am_coordinator)
{
#if MAC_LAYER 
    hal_subregister_write(SR_I_AM_COORD, i_am_coordinator);
#endif // MAC_LAYER
}


/*  
    This function will set the PANID used by the address filter.
  
    @param  new_pan_id Desired PANID. Can be any value from 0x0000 to 0xFFFF
 */
void radio_set_panid(uint16_t new_pan_id)
{

    u8 pan_byte = new_pan_id & 0xFF; // Extract new_pan_id_7_0.
    hal_register_write(RG_PAN_ID_0, pan_byte);

    pan_byte = (new_pan_id >> 8*1) & 0xFF;  // Extract new_pan_id_15_8.
    hal_register_write(RG_PAN_ID_1, pan_byte);
    
    panid = new_pan_id;
}

u16 radio_get_panid(void)
{
    u16 temp = 0;
    if(panid)
    {
        return panid;
    }
    else
    {    
        temp = hal_register_read(RG_PAN_ID_1);
        temp<<=8;
        temp |= hal_register_read(RG_PAN_ID_0);
        return temp;
    }
}


/*  
    This function will set the short address used by the address filter.
 
    @param  new_short_address Short address to be used by the address filter.
 */
void radio_set_short_address(uint16_t new_short_address)
{

    u8 short_address_byte = new_short_address & 0xFF; // Extract short_address_7_0.
    hal_register_write(RG_SHORT_ADDR_0, short_address_byte);

    short_address_byte = (new_short_address >> 8*1) & 0xFF; // Extract short_address_15_8.
    hal_register_write(RG_SHORT_ADDR_1, short_address_byte);
    
    short_address = new_short_address;
}

u16 radio_get_short_address(void)
{
    u16 temp = 0;
    if(short_address)
    {
        return short_address;
    }
    else
    {    
        temp = hal_register_read(RG_SHORT_ADDR_1);
        temp<<=8;
        temp |= hal_register_read(RG_SHORT_ADDR_0);
        return temp;
    }
}

void radio_set_remote_address(u16 remote_address)
{
    remote_node_address = remote_address;
}

u16 radio_get_remote_address(void)
{
    return remote_node_address;
}


/*  
    This function will set a new extended address to be used by the
    address filter.
  
    @param  extended_address Extended address to be used by the address filter.
 */
void radio_set_long_address(u8 *extended_address)
{
    u8 i;

    for (i=0;i<8;i++)
    {
       hal_register_write(RG_IEEE_ADDR_0+i, *extended_address++);
    }
}


/* 
   Returns a random number, composed of bits from the radio's
   random number generator.  Note that the radio must be in a receive
   mode for this to work, otherwise the library rand() function is
   used.

   @param bits Number of bits of random data to return.  This function
   will return an even number of random bits, equal to or less than bits.
 */
u8 radio_random(u8 bits)
{
    u8 val=0;
    u8 regval;
    u8 i;

    i = radio_get_trx_state();
    if ((radio_get_part_num() == RF231) &&
        (i == RX_ON ||
         i == RX_AACK_ON))       // Must be in rx to get random numbers
    {
        // Random number generator on-board
        // has two random bits each read
        for (i=0;i<bits/2;i++)
        {
            regval = hal_subregister_read(SR_RND_VALUE);
            val = (val << 2) | regval;
        }
        return val;
    }
    else
        // use library function.
        return rand();
}


/*EOF*/
