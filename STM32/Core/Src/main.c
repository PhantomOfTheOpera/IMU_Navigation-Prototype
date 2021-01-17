/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * <h2><center>&copy; Copyright (c) 2020 STMicroelectronics.
  * All rights reserved.</center></h2>
  *
  * This software component is licensed by ST under BSD 3-Clause license,
  * the "License"; You may not use this file except in compliance with the
  * License. You may obtain a copy of the License at:
  *                        opensource.org/licenses/BSD-3-Clause
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "i2c.h"
#include "spi.h"
#include "usb_device.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "usbd_cdc_if.h"
#include "mems.h"
#include "stm32f3_discovery_gyroscope.h"
#include "math.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */
typedef enum state_t {ACCEL_DRDY_S, MAGNET_DRDY_S, GYRO_DRDY_S,
					  TRANSMIT_READY_S, IDLE_S, ERROR_S} state_t;
typedef enum sensor_t {ACCEL=0,
					   MAGN=1,
					   GYRO=2} sensor_t;

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
#define MAX_STR_OUT 200
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */
HAL_StatusTypeDef status;
uint8_t res[6], accel_flag = 0, magn_flag = 0, gyro_flag = 0,
		acc_transmit = 0, magn_transmit = 0, gyro_transmit = 0;
uint16_t Lens[3] = {0}, MaxLens[3] = {0};
char str1[MAX_STR_OUT]={0};
int16_t AccelData[3] = {0}, MagData[3] = {0}, MaxAccelData[3] = {0}, MaxMagData[3] = {0};
float GyroData[3] = {0.0f}, MaxGyroData = {0.0f};

//state_t state = IDLE_S;
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_NVIC_Init(void);
/* USER CODE BEGIN PFP */
void error(void);
void success(void);
static uint8_t I2C_Read(uint16_t Addr, uint8_t Reg);
static void I2C_Write(uint16_t Addr, uint8_t Reg, uint8_t Value);
uint8_t I2C_ReadID(uint16_t Addr);
void Accel_Ini(void);
void Accel_GetXYZ(int16_t* pData);
void Mag_Ini(void);
void Mag_GetXYZ(int16_t* pData);
/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

//LED Indication

void error(void) {
	HAL_GPIO_WritePin(LED6_GPIO_Port, LED6_Pin, GPIO_PIN_RESET);
	HAL_GPIO_WritePin(LED3_GPIO_Port, LED3_Pin, GPIO_PIN_SET);
}

void success(void) {
	HAL_GPIO_WritePin(LED3_GPIO_Port, LED3_Pin, GPIO_PIN_RESET);
	HAL_GPIO_WritePin(LED6_GPIO_Port, LED6_Pin, GPIO_PIN_SET);
}

//I2C Operations

static uint8_t I2C_Read(uint16_t Addr, uint8_t Reg) {
	HAL_StatusTypeDef status = HAL_OK;
	uint8_t value = 0;
	status = HAL_I2C_Mem_Read(&hi2c1, Addr, Reg, I2C_MEMADD_SIZE_8BIT, &value, 1, 0x10000);
	if(status != HAL_OK) error();
	else success();
	return value;
}

static void I2C_Write(uint16_t Addr, uint8_t Reg, uint8_t Value) {
	HAL_StatusTypeDef status = HAL_OK;
	status = HAL_I2C_Mem_Write(&hi2c1, Addr, (uint16_t)Reg, I2C_MEMADD_SIZE_8BIT, &Value, 1, 0x10000);
	if(status != HAL_OK) error();
	else success();
}

uint8_t I2C_ReadID(uint16_t Addr) {
	uint8_t ctrl = 0x00;
	ctrl = I2C_Read(Addr,0x0F);
	return ctrl;
}

//Accelerometer Operations

void Accel_Ini(void) {
	uint8_t ctrl;
	if (I2C_ReadID(0x33)==0x33)	{
		ctrl=0b10010111;
		I2C_Write(0x32,0x20,ctrl);
		ctrl=0b00010000;
		I2C_Write(0x32,0x22,ctrl);
		ctrl=0b00001000;
		I2C_Write(0x32,0x23,ctrl);
		ctrl=0b00000000;
		I2C_Write(0x32,0x25,ctrl);
	}
	HAL_Delay(500);
}

void Accel_GetXYZ(int16_t* pData) {
	HAL_StatusTypeDef status = HAL_OK;
	uint8_t buffer[6];
	uint8_t i=0;

	status = HAL_I2C_Mem_Read(&hi2c1, 0x32, 0x28|0x80, I2C_MEMADD_SIZE_8BIT, buffer, 6, 0x10000);
 	if(status != HAL_OK) error();
	else success();

	for(i=0;i<3;i++) {
		pData[i]=((int16_t)((uint16_t)buffer[2*i+1]<<8)+buffer[2*i]) / 16;
	}
}

//Magnetometer Operations

void Mag_Ini(void) {
	uint8_t ctrl;
	if (I2C_ReadID(0x3C)==0x3C)	{
		ctrl=0b00011100;
		I2C_Write(0x3C,0x00,ctrl);
		ctrl=0b11100000;
		I2C_Write(0x3C,0x01,ctrl);
		ctrl=0b00000000;
		I2C_Write(0x3C,0x02,ctrl);
	}
	HAL_Delay(500);
}

void Mag_GetXYZ(int16_t* pData) {
	uint8_t buffer[6];

	HAL_StatusTypeDef status = HAL_OK;
	status = HAL_I2C_Mem_Read(&hi2c1, 0x3C, 0x03|0x80, I2C_MEMADD_SIZE_8BIT, buffer, 6, 0x10000);
 	if(status != HAL_OK) error();
	else success();
	pData[0]=((int16_t)((uint16_t)buffer[0]<<8)+buffer[1]);
	pData[1]=((int16_t)((uint16_t)buffer[4]<<8)+buffer[5]);
	pData[2]=((int16_t)((uint16_t)buffer[2]<<8)+buffer[3]);
}


// Math

void GetAndCompareLen(sensor_t Type) {
	switch (Type) {
	case ACCEL: {

	}
	case MAGN: {

	}
	case GYRO: {

	}
	default:
		error();
		return NULL;
	}
}

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_USB_DEVICE_Init();
  MX_I2C1_Init();
  MX_SPI1_Init();

  /* Initialize interrupts */
  MX_NVIC_Init();
  /* USER CODE BEGIN 2 */
  HAL_NVIC_DisableIRQ(EXTI4_IRQn);
  Accel_Ini();
  Mag_Ini();
  BSP_GYRO_Init();
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  Accel_GetXYZ(AccelData);
  HAL_NVIC_EnableIRQ(EXTI4_IRQn);
  BSP_GYRO_EnableIT(L3GD20_INT2);
  while (1) {
	  if (accel_flag) {
		  HAL_NVIC_DisableIRQ(EXTI4_IRQn);
		  HAL_GPIO_WritePin(LED5_GPIO_Port, LED5_Pin, GPIO_PIN_SET);
		  Accel_GetXYZ(AccelData);
		  HAL_Delay(10);
		  accel_flag = 0;
		  acc_transmit = 1;
		  HAL_NVIC_EnableIRQ(EXTI4_IRQn);
	  }
	  if (magn_flag) {
		  HAL_NVIC_DisableIRQ(EXTI2_TSC_IRQn);
		  HAL_GPIO_WritePin(LED4_GPIO_Port, LED4_Pin, GPIO_PIN_SET);
		  Mag_GetXYZ(MagData);
		  magn_flag = 0;
		  magn_transmit = 1;
		  HAL_NVIC_EnableIRQ(EXTI2_TSC_IRQn);
	  }
	  if (gyro_flag) {
		  BSP_GYRO_DisableIT(L3GD20_INT2);
		  BSP_GYRO_GetXYZ(GyroData);
		  gyro_flag = 0;
		  gyro_transmit = 1;
		  BSP_GYRO_EnableIT(L3GD20_INT2);
	  }
	  if (magn_transmit && acc_transmit && gyro_transmit) {
		  HAL_NVIC_DisableIRQ(EXTI4_IRQn);
		  HAL_NVIC_DisableIRQ(EXTI2_TSC_IRQn);
		  BSP_GYRO_DisableIT(L3GD20_INT2);
		  sprintf(str1, "%d;%5d;%5d;%5d;%4d;%4d;%4d;%8d;%8d;%8d\n", HAL_GetTick(), AccelData[0], AccelData[1], AccelData[2],
				  MagData[0], MagData[1], MagData[2], (int)GyroData[0], (int)GyroData[1], (int)GyroData[2]);
		  CDC_Transmit_FS((uint8_t*)str1, strlen(str1));
		  acc_transmit = magn_transmit = gyro_transmit = 0;
		  BSP_GYRO_EnableIT(L3GD20_INT2);
		  HAL_NVIC_EnableIRQ(EXTI2_TSC_IRQn);
		  HAL_NVIC_EnableIRQ(EXTI4_IRQn);
	  }
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};
  RCC_PeriphCLKInitTypeDef PeriphClkInit = {0};

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI|RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.HSEPredivValue = RCC_HSE_PREDIV_DIV1;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL9;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }
  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
  PeriphClkInit.PeriphClockSelection = RCC_PERIPHCLK_USB|RCC_PERIPHCLK_I2C1;
  PeriphClkInit.I2c1ClockSelection = RCC_I2C1CLKSOURCE_HSI;
  PeriphClkInit.USBClockSelection = RCC_USBCLKSOURCE_PLL_DIV1_5;
  if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInit) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief NVIC Configuration.
  * @retval None
  */
static void MX_NVIC_Init(void)
{
  /* EXTI4_IRQn interrupt configuration */
  HAL_NVIC_SetPriority(EXTI4_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(EXTI4_IRQn);
  /* EXTI2_TSC_IRQn interrupt configuration */
  HAL_NVIC_SetPriority(EXTI2_TSC_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(EXTI2_TSC_IRQn);
  /* EXTI1_IRQn interrupt configuration */
  HAL_NVIC_SetPriority(EXTI1_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(EXTI1_IRQn);
}

/* USER CODE BEGIN 4 */
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
	switch (GPIO_Pin) {
	case GPIO_PIN_2: {
		magn_flag = 1;
	}
	case GPIO_PIN_4: {
		accel_flag = 1;
	}
	case GPIO_PIN_1: {
		gyro_flag = 1;
	}
	default:
		;
	}
}

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */

  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     tex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
