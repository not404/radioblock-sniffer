################################################################################
# Automatically-generated file. Do not edit!
################################################################################

-include ../makefile.init

RM := rm -rf

# All of the sources participating in the build are defined here
-include sources.mk
-include subdir.mk
-include radio/subdir.mk
-include drivers/subdir.mk
-include objects.mk

ifneq ($(MAKECMDGOALS),clean)
ifneq ($(strip $(C_DEPS)),)
-include $(C_DEPS)
endif
endif

-include ../makefile.defs

# Add inputs and outputs from these tool invocations to the build variables 

# All Target
all: RadioBlocksSniffer.axf

# Tool invocations
RadioBlocksSniffer.axf: $(OBJS) $(USER_OBJS)
	@echo 'Building target: $@'
	@echo 'Invoking: MCU Linker'
	arm-none-eabi-gcc -nostdlib -L"C:\development\sniffer\CMSISv2p00_LPC11xx\Debug" -Xlinker -Map="RadioBlocksSniffer.map" -Xlinker --gc-sections -mcpu=cortex-m0 -mthumb -T "RadioBlocksSniffer_Debug.ld" -o"RadioBlocksSniffer.axf" $(OBJS) $(USER_OBJS) $(LIBS)
	@echo 'Finished building target: $@'
	@echo ' '
	$(MAKE) --no-print-directory post-build

# Other Targets
clean:
	-$(RM) $(OBJS)$(C_DEPS)$(EXECUTABLES) RadioBlocksSniffer.axf
	-@echo ' '

post-build:
	-@echo 'Performing post-build steps'
	-arm-none-eabi-size "RadioBlocksSniffer.axf"; # arm-none-eabi-objcopy -O binary "RadioBlocksSniffer.axf" "RadioBlocksSniffer.bin" ; checksum -p LPC1114_201 -d "RadioBlocksSniffer.bin";
	-@echo ' '

.PHONY: all clean dependents
.SECONDARY: post-build

-include ../makefile.targets
