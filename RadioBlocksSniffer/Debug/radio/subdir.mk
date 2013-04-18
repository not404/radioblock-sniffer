################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../radio/hal.c \
../radio/radio.c 

OBJS += \
./radio/hal.o \
./radio/radio.o 

C_DEPS += \
./radio/hal.d \
./radio/radio.d 


# Each subdirectory must supply rules for building sources it contributes
radio/%.o: ../radio/%.c
	@echo 'Building file: $<'
	@echo 'Invoking: MCU C Compiler'
	arm-none-eabi-gcc -D__REDLIB__ -DCONFIG_UART_ENABLE_INTERRUPT=1 -DSNIFER_MODE=1 -DCONFIG_UART_DEFAULT_UART_IRQHANDLER=1 -D__USE_CMSIS -DCONFIG_ENABLE_DRIVER_UART=1 -DDEBUG -D__CODE_RED -I"/Users/egnoske/CMD Projects/work/sniffer/CMSISv2p00_LPC11xx/inc" -I"/Users/egnoske/CMD Projects/work/sniffer/RadioBlocksSniffer/drivers" -I"/Users/egnoske/CMD Projects/work/sniffer/RadioBlocksSniffer/radio" -O0 -g3 -Wall -c -fmessage-length=0 -fno-builtin -ffunction-sections -fdata-sections -mcpu=cortex-m0 -mthumb -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@:%.o=%.d)" -o"$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


