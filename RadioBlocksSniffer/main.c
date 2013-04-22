/*
===============================================================================
 Name        : main.c
 Author      : 
 Version     :
 Copyright   : Copyright (C) 
 Description : main definition
===============================================================================
*/

#ifdef __USE_CMSIS
#include "LPC11xx.h"
#endif


#include <stdbool.h>
#include <string.h>
#include "hal.h"
#include "radio.h"
#include "rf231.h"

#include "timer16.h"
#include "uart.h"


extern uint8_t  UARTBuffer[BUFSIZE];
extern uint32_t UARTCount;


u8 rx_mode;
_Bool spi_spinlock;

void writeOneByte(uint8_t ch);
void convertTwoBytes(void);
void convertOneByte(void);
void spaces(u8 spaces);

typedef enum{
				fr_len  = 99,
				fcf		= 0,
				seq		= 1,
				panid	= 3,
				macdst	= 5,
				macsrc	= 7,
				nwkfcf	= 8,
				nwkseq	= 9,
				nwksrc	= 10,
				nwkdst	= 12,
				payload = 13,
				lqi		= 14,
				rssi 	= 15}frameState_t;

int main(void)
{
	u8 len = 0;
	u8 channel = 11;
	u8 ackFlag = 0;
	frameState_t fState = fr_len;

	// Global variables for circular buffer and sniffing
	start = 0;
	end = 0;

	// Init GPIO, SPI, Radio
	radio_init();

	// Setup the UART.
	UARTInit(115200);
	rxdFlag = 0;

	// Set a default channel
	radio_set_channel(15);
	channel = radio_get_channel();

    while(1)
    {
    	// Check to see if channel changed
    	if(rxdFlag)
    	{
    		if(UARTBuffer[0] == 'C')
    		{
    			channel = (UARTBuffer[1] - 0x30) * 10;
    			channel += (UARTBuffer[2] - 0x30);
    			radio_set_channel(channel);
    			rxdFlag = 0;
    			UARTCount = 0;
    			memset(UARTBuffer, 0, BUFSIZE);
    			// DEBUG
    			//channel = radio_get_channel();
    		}
    		else if(UARTBuffer[0] == 'G')
    		{
    			channel = radio_get_channel();
    			rxdFlag = 0;
    			UARTCount = 0;
    			memset(UARTBuffer, 0, BUFSIZE);
    			// Send the channel over the uart
    			while ( !(LPC_UART->LSR & LSR_THRE) );
    				LPC_UART->THR = channel;
    		}
    	}

    	/*
    	 * The parsing is specific to work with the Python GUI. Could easily change...
    	 */
    	if(frame_received != 0)
    	{
        	DBG1on();

        	while(end != start)
        	{
        		// Start grabbing bytes from the circular buffer.
				len = readByte();
				if(len == 5)
					ackFlag = 1;

				while(len != 0)
				{
					// Do some minimal formatting so that 2 byte fields:
					// FCF, panid, addresses are byte swapped.
					switch(fState)
					{
						case fr_len:
							writeOneByte(0x0a);
							writeOneByte(0x0b);
							writeOneByte(0x0c);
							writeOneByte(0x0d);
							writeOneByte(len);
							fState = fcf;
							break;
						// FCF
						case fcf:
							convertTwoBytes();
							fState = seq;
							len -= 2;
							break;
						case seq:
							// ETG spaces(2);
							convertOneByte();
							if(!ackFlag)
							{
								fState = panid;
							}
							else
							{
								fState = lqi;
							}
							len -= 1;
							break;
						// panid
						case panid:
							// ETG spaces(3);
							convertTwoBytes();
							fState = macdst;
							len -= 2;
							break;
						// mac dest
						case macdst:
							// ETG spaces(3);
							convertTwoBytes();
							fState = macsrc;
							len -= 2;
							break;
						// mac src
						case macsrc:
							// ETG spaces(4);
							convertTwoBytes();
							fState = nwkfcf;
							len -= 2;
							break;
						case nwkfcf:
							// ETG spaces(8);
							convertOneByte();
							fState = nwkseq;
							len -= 1;
							break;
						case nwkseq:
							// ETG spaces(2);
							convertOneByte();
							fState = nwksrc;
							len -= 1;
							break;
						// nwk src
						case nwksrc:
							// ETG spaces(2);
							convertTwoBytes();
							fState = nwkdst;
							len -= 2;
							break;
						// nwk dst
						case nwkdst:
							// ETG spaces(3);
							convertTwoBytes();
							fState = payload;
							len -= 2;
							// ETG spaces(3);
							break;
						// Payload
						case payload:
							convertOneByte();
							len--;
							if(len == 2)
								fState = lqi;
							break;
						// LQI
						case lqi:
							// ETG if(!ackFlag)
								// ETG spaces(2);
							// ETG else
							if(ackFlag)
							{
								// ETG spaces(62);
								ackFlag = 0;
							}
							convertOneByte();
							fState = rssi;
							len--;
							// ETG spaces(1);
							break;
						// rssi
						case rssi:
							convertOneByte();
							fState = fr_len;
							len--;
							break;
					};
        		}
    					// Put a carriage return after each line to make it readable
    					while ( !(LPC_UART->LSR & LSR_THRE) );
    					LPC_UART->THR = '\n';
        	}
					frame_received = 0;
					DBG1off();
    	}
    }

	return 0 ;
}

/* ETG
// Functions for Hex Ascii conversion and byte formatting for the sniffer display.
void spaces(u8 spaces)
{
	u8 i;

	for(i=0; i< spaces; i++)
	{
		// Put a carriage return after each line to make it readable
		while ( !(LPC_UART->LSR & LSR_THRE) );
		LPC_UART->THR = ' ';
	}
}
*/

void writeOneByte(uint8_t ch)
{
	u8 rawByte = ch;
	u8 asciiByte1, asciiByte2;

	// Shift down and convert the MSNibble
	if((0x0F & (rawByte >> 4)) < 10)
		asciiByte1 = (0x0F & (rawByte >> 4)) + '0';		// 0 - 9
	else
		asciiByte1 = (0x0F & (rawByte >> 4)) + 87;		// a - f
	while ( !(LPC_UART->LSR & LSR_THRE) );
	LPC_UART->THR = asciiByte1;

	// Convert the LSNibble
	if((0x0F & rawByte)  < 10 )
		asciiByte2 = (0x0F & rawByte) + '0';			// 0 - 9
	else
		asciiByte2 = (0x0F & rawByte) + 87;				// a - f
	while ( !(LPC_UART->LSR & LSR_THRE) );
	LPC_UART->THR = asciiByte2;
}

void convertOneByte(void)
{
	u8 rawByte;
	u8 asciiByte1, asciiByte2;

	rawByte = readByte();

	// Shift down and convert the MSNibble
	if((0x0F & (rawByte >> 4)) < 10)
		asciiByte1 = (0x0F & (rawByte >> 4)) + '0';		// 0 - 9
	else
		asciiByte1 = (0x0F & (rawByte >> 4)) + 87;		// a - f
	while ( !(LPC_UART->LSR & LSR_THRE) );
	LPC_UART->THR = asciiByte1;

	// Convert the LSNibble
	if((0x0F & rawByte)  < 10 )
		asciiByte2 = (0x0F & rawByte) + '0';			// 0 - 9
	else
		asciiByte2 = (0x0F & rawByte) + 87;				// a - f
	while ( !(LPC_UART->LSR & LSR_THRE) );
	LPC_UART->THR = asciiByte2;
}
void convertTwoBytes(void)
{
	u8 dat[4];
	u8 rawByte;
	u8 i;

	rawByte = readByte();

	// The first byte is passed in and needs conversion

	// Shift down and convert the MSNibble
	if((0x0F & (rawByte >> 4)) < 10)
		dat[2] = (0x0F & (rawByte >> 4)) + '0';		// 0 - 9
	else
		dat[2] = (0x0F & (rawByte >> 4)) + 87;		// a - f

	// Convert the LSNibble
	if((0x0F & rawByte)  < 10 )
		dat[3] = (0x0F & rawByte) + '0';			// 0 - 9
	else
		dat[3] = (0x0F & rawByte) + 87;				// a - f

	// Read the second byte and convert
	rawByte = readByte();

	// Shift down and convert the MSNibble
	if((0x0F & (rawByte >> 4)) < 10)
		dat[0] = (0x0F & (rawByte >> 4)) + '0';		// 0 - 9
	else
		dat[0] = (0x0F & (rawByte >> 4)) + 87;		// a - f

	// Convert the LSNibble
	if((0x0F & rawByte)  < 10 )
		dat[1] = (0x0F & rawByte) + '0';			// 0 - 9
	else
		dat[1] = (0x0F & rawByte) + 87;				// a - f

	for(i=0; i<4; i++)
	{
		while ( !(LPC_UART->LSR & LSR_THRE) );
		LPC_UART->THR = dat[i];
	}
}

// Functions for the circular UART buffer
void writeByte(uint8_t data)
{
	// Put the byte into the buffer.
	sniffBuff[start] = data;

	// Adjust the start value if it wraps around.
	if((start + 1) < circSize)
		start += 1;
	else
		start = 0;
}

uint8_t readByte(void)
{
	uint8_t data;

	data = sniffBuff[end];

	if((end + 1) < circSize)
		end += 1;
	else
		end = 0;

	return data;
}
