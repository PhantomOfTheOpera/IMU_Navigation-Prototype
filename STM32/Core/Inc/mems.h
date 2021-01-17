/*
 * mems.h
 *
 *  Created on: Nov 1, 2020
 *      Author: osobkovych
 */

#ifndef INC_MEMS_H_
#define INC_MEMS_H_

#include "stm32f3xx_hal.h"

I2C_HandleTypeDef hi2c1;

void error(void);
void success(void);
static uint8_t I2C_Read(uint16_t Addr, uint8_t Reg);
static void I2C_Write(uint16_t Addr, uint8_t Reg, uint8_t Value);
uint8_t I2C_ReadID(uint16_t Addr);
void Accel_Ini(void);
void Accel_GetXYZ(int16_t* pData);
void Mag_Ini(void);
void Mag_GetXYZ(int16_t* pData);


#endif /* INC_MEMS_H_ */
