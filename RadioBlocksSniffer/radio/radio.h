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
  $Id: radio.h,v 1.1 2012/04/25 17:42:57 cvsuser Exp $
*/

#ifndef RADIO_H
#define RADIO_H
/*============================ INCLUDE =======================================*/
#include "type.h"
#include <stdint.h>
#include <stdbool.h>

/*============================ MACROS ========================================*/
#define RF230_REVA                              ( 1 )
#define RF230_REVB                              ( 2 )
#define SUPPORTED_MANUFACTURER_ID               ( 31 )
#define RF2xx_SUPPORTED_INTERRUPT_MASK          ( 0x0C )	// Both the TRX_END (3) and RX_START (2)
#define RF2xx_TRXEND_INTERRUPT_MASK          	( 0x08 )
#define RF2xx_MAX_TX_FRAME_LENGTH               ( 127 ) // 127 Byte PSDU.

#define TX_PWR_3DBM                             ( 0 )
#define TX_PWR_17_2DBM                          ( 15 )

#define BATTERY_MONITOR_HIGHEST_VOLTAGE         ( 15 )
#define BATTERY_MONITOR_VOLTAGE_UNDER_THRESHOLD ( 0 )
#define BATTERY_MONITOR_HIGH_VOLTAGE            ( 1 )
#define BATTERY_MONITOR_LOW_VOLTAGE             ( 0 )

#define FTN_CALIBRATION_DONE                    ( 0 )
#define PLL_DCU_CALIBRATION_DONE                ( 0 )
#define PLL_CF_CALIBRATION_DONE                 ( 0 )
/*============================ TYPEDEFS ======================================*/

extern _Bool frame_received;

/*  
    This macro defines the start value for the RADIO_* status constants.
  
    It was chosen to have this macro so that the user can define where
    the status returned from the TAT starts. This can be useful in a
    system where numerous drivers are used, and some range of status codes
    are occupied.
 */
#define RADIO_STATUS_START_VALUE                  ( 0x40 )

/*  
    This enumeration defines the possible return values for the TAT API
    functions.
  
    These values are defined so that they should not collide with the
    return/status codes defined in the IEEE 802.15.4 standard.
 */
typedef enum
{
    RADIO_SUCCESS = RADIO_STATUS_START_VALUE,   // The requested service was performed successfully.
    RADIO_UNSUPPORTED_DEVICE,                   // The connected device is not an Atmel AT86RF230.
    RADIO_INVALID_ARGUMENT,                     // One or more of the supplied function arguments are invalid.
    RADIO_TIMED_OUT,                            // The requested service timed out.
    RADIO_WRONG_STATE,                          // The end-user tried to do an invalid state transition.
    RADIO_BUSY_STATE,                           // The radio transceiver is busy receiving or transmitting.
    RADIO_STATE_TRANSITION_FAILED,              // The requested state transition could not be completed.
    RADIO_CCA_IDLE,                             // Channel in idle. Ready to transmit a new frame.
    RADIO_CCA_BUSY,                             // Channel busy.
    RADIO_TRX_BUSY,                             // Transceiver is busy receiving or transmitting data.
    RADIO_BAT_LOW,                              // Measured battery voltage is lower than voltage threshold.
    RADIO_BAT_OK,                               // Measured battery voltage is above the voltage threshold.
    RADIO_CRC_FAILED,                           // The CRC failed for the actual frame.
    RADIO_CHANNEL_ACCESS_FAILURE,               // The channel access failed during the auto mode.
    RADIO_NO_ACK,                               // No acknowledge frame was received.
}radio_status_t;

#define TRAC_SUCCESS                0
#define TRAC_SUCCESS_DATA_PENDING   1
#define TRAC_SUCCESS_WAIT_FOR_ACK   2
#define TRAC_CHANNEL_ACCESS_FAILURE 3
#define TRAC_NO_ACK                 5
#define TRAC_INVALID                7

/*  
    This enumeration defines the possible modes available for the
    Clear Channel Assessment algorithm.
  
    These constants are extracted from the datasheet.
 */
typedef enum
{
    CCA_ED                    = 0,    // Use energy detection above threshold mode.
    CCA_CARRIER_SENSE         = 1,    // Use carrier sense mode.
    CCA_CARRIER_SENSE_WITH_ED = 2     // Use a combination of both energy detection and carrier sense.
}radio_cca_mode_t;

/*  
    This enumeration defines the possible CLKM speeds.
  
    These constants are extracted from the RF231 datasheet.
 */
typedef enum
{
    CLKM_DISABLED      = 0,
    CLKM_1MHZ          = 1,
    CLKM_2MHZ          = 2,
    CLKM_4MHZ          = 3,
    CLKM_8MHZ          = 4,
    CLKM_16MHZ         = 5
}radio_clkm_speed_t;

typedef void (*radio_rx_callback) (u16 data);

/*============================ PROTOTYPES ====================================*/

radio_status_t  radio_init(void);

u8              radio_get_part_num(void);

u8              radio_get_saved_rssi_value(void);
u8              radio_get_saved_lqi_value(void);
u8              radio_get_channel(void);
radio_status_t  radio_set_channel(u8 channel);
u8              radioGetTxPowerLevel(void);
radio_status_t  radio_set_tx_power_level(u8 powerLevel);

u8              radioGetCcaMode(void);
u8              radioGetEdThreshold(void);
radio_status_t  radio_get_rssi_value(u8 *rssi);

u8              radioGetClockSpeed(void);

u8              radio_is_busy(void);
u8              radio_get_trx_state(void);
radio_status_t  radio_set_trx_state(u8 newState);
radio_status_t  radioEnterSleepMode(void);
radio_status_t  radioLeaveSleepMode(void);
void            radio_reset_state_machine(void);
void            radio_reset_trx(void);

void 				    radio_use_auto_tx_crc(void);
radio_status_t  radio_send_data(u8 dataLength, u8 *data);

void            radio_set_device_role(_Bool iAmCoordinator);
void            radio_set_panid(u16 newPanId);
void            radio_set_short_address(u16 newShortAddress);
void            radio_set_long_address(u8 *extendedAddress);

u8              radio_random(u8 bits);

#endif //RADIO_H
/*EOF*/
