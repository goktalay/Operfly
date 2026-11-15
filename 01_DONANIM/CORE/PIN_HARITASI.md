# Operfly Core - işlemci pin haritası (STM32H753IIK6)

Bu dosya `pin_atamalari.csv` dosyasından `10_ORTAK_ARACLAR/kicad/pin_dogrula.py` ile üretilir; elle düzenlemeyin.
Her atama, KiCad kütüphanesindeki `STM32H753IIKx` sembolünün pin işlevlerine karşı doğrulanmıştır.

- Kılıf: `Package_BGA:UFBGA-201_10x10mm_Layout15x15_P0.65mm`
- Atanan pin: 97
- Boş kalan G/Ç pini: 43


## Ethernet (RMII, 100 Mbit)

| Sinyal | Pin | Top | İşlev | Not |
|---|---|---|---|---|
| ETH_REF_CLK | PA1 | N2 | ETH_REF_CLK | PHY'den 50 MHz |
| ETH_MDIO | PA2 | P2 | ETH_MDIO |  |
| ETH_MDC | PC1 | M3 | ETH_MDC |  |
| ETH_CRS_DV | PA7 | R3 | ETH_CRS_DV |  |
| ETH_RXD0 | PC4 | N5 | ETH_RXD0 |  |
| ETH_RXD1 | PC5 | P5 | ETH_RXD1 |  |
| ETH_TX_EN | PG11 | B9 | ETH_TX_EN |  |
| ETH_TXD0 | PG13 | A8 | ETH_TXD0 |  |
| ETH_TXD1 | PG12 | B8 | ETH_TXD1 |  |
| ETH_PPS_OUT | PB5 | A6 | ETH_PPS_OUT | PTP saatinden PPS çıkışı |
| PHY_NRST | PG14 | A7 | GPIO |  |
| PHY_INT | PG15 | B7 | GPIO | kesme girişi |

## CAN FD

| Sinyal | Pin | Top | İşlev | Not |
|---|---|---|---|---|
| CAN_A_RX | PD0 | B12 | FDCAN1_RX | Operfly Bus CAN A |
| CAN_A_TX | PD1 | C12 | FDCAN1_TX |  |
| CAN_A_STB | PD3 | D11 | GPIO | alıcı-verici bekleme |
| CAN_B_RX | PB12 | P12 | FDCAN2_RX | Operfly Bus CAN B |
| CAN_B_TX | PB13 | P13 | FDCAN2_TX |  |
| CAN_B_STB | PD4 | D10 | GPIO | alıcı-verici bekleme |

## IMU 1 (ICM-42688-P)

| Sinyal | Pin | Top | İşlev | Not |
|---|---|---|---|---|
| IMU1_SCK | PA5 | P4 | SPI1_SCK | her IMU ayrı SPI hattında |
| IMU1_MISO | PA6 | P3 | SPI1_MISO |  |
| IMU1_MOSI | PD7 | A11 | SPI1_MOSI |  |
| IMU1_CS | PI9 | D3 | GPIO |  |
| IMU1_DRDY | PI10 | E3 | GPIO | kesme girişi |

## IMU 2 (BMI088)

| Sinyal | Pin | Top | İşlev | Not |
|---|---|---|---|---|
| IMU2_SCK | PI1 | D14 | SPI2_SCK |  |
| IMU2_MISO | PI2 | C14 | SPI2_MISO |  |
| IMU2_MOSI | PI3 | C13 | SPI2_MOSI |  |
| IMU2_CS_ACC | PI4 | D4 | GPIO |  |
| IMU2_CS_GYR | PI8 | D2 | GPIO |  |
| IMU2_INT_ACC | PI5 | C4 | GPIO | kesme girişi |
| IMU2_INT_GYR | PI6 | C3 | GPIO | kesme girişi |

## IMU 3 (ICM-45686)

| Sinyal | Pin | Top | İşlev | Not |
|---|---|---|---|---|
| IMU3_SCK | PE2 | A2 | SPI4_SCK |  |
| IMU3_MISO | PE5 | B2 | SPI4_MISO |  |
| IMU3_MOSI | PE6 | B3 | SPI4_MOSI |  |
| IMU3_CS | PE4 | B1 | GPIO |  |
| IMU3_DRDY | PE3 | A1 | GPIO | kesme girişi |

## FRAM

| Sinyal | Pin | Top | İşlev | Not |
|---|---|---|---|---|
| FRAM_SCK | PF7 | K1 | SPI5_SCK |  |
| FRAM_MISO | PF8 | L3 | SPI5_MISO |  |
| FRAM_MOSI | PF9 | L2 | SPI5_MOSI |  |
| FRAM_CS | PF6 | K2 | GPIO |  |

## I2C sensörler A

| Sinyal | Pin | Top | İşlev | Not |
|---|---|---|---|---|
| I2C_A_SCL | PF14 | R7 | I2C4_SCL | barometre 1, pusula, güvenli eleman |
| I2C_A_SDA | PF15 | P7 | I2C4_SDA |  |

## I2C sensörler B

| Sinyal | Pin | Top | İşlev | Not |
|---|---|---|---|---|
| I2C_B_SCL | PF1 | H3 | I2C2_SCL | barometre 2 (ayrı hat) |
| I2C_B_SDA | PF0 | E2 | I2C2_SDA |  |

## I2C sensörler A

| Sinyal | Pin | Top | İşlev | Not |
|---|---|---|---|---|
| SE_NRST | PH4 | H4 | GPIO | güvenli eleman sıfırlama |

## IO işlemcisi

| Sinyal | Pin | Top | İşlev | Not |
|---|---|---|---|---|
| IO_UART_TX | PC6 | H15 | USART6_TX | IO/failsafe işlemcisine |
| IO_UART_RX | PC7 | G15 | USART6_RX |  |
| IO_NRST | PG6 | J15 | GPIO | IO işlemcisini sıfırlar (yazılım güncelleme) |
| IO_BOOT0 | PG8 | H14 | GPIO |  |
| N_ARMED | PH5 | J4 | GPIO | silahlanma durumu |

## Hata ayıklama

| Sinyal | Pin | Top | İşlev | Not |
|---|---|---|---|---|
| DBG_UART_TX | PD8 | P15 | USART3_TX | konsol |
| DBG_UART_RX | PD9 | P14 | USART3_RX |  |
| SWDIO | PA13 | A15 | DEBUG_JTMS-SWDIO |  |
| SWCLK | PA14 | A14 | DEBUG_JTCK-SWCLK |  |
| SWO | PB3 | A10 | DEBUG_JTDO-SWO |  |

## USB

| Sinyal | Pin | Top | İşlev | Not |
|---|---|---|---|---|
| USB_DM | PA11 | C15 | USB_OTG_FS_DM | servis portu |
| USB_DP | PA12 | B15 | USB_OTG_FS_DP |  |
| USB_VBUS | PA9 | E15 | USB_OTG_FS_VBUS |  |

## microSD (öneri)

| Sinyal | Pin | Top | İşlev | Not |
|---|---|---|---|---|
| SD_D0 | PC8 | G14 | SDMMC1_D0 | uçuş kaydı için |
| SD_D1 | PC9 | F14 | SDMMC1_D1 |  |
| SD_D2 | PC10 | B14 | SDMMC1_D2 |  |
| SD_D3 | PC11 | B13 | SDMMC1_D3 |  |
| SD_CK | PC12 | A12 | SDMMC1_CK |  |
| SD_CMD | PD2 | D12 | SDMMC1_CMD |  |
| SD_DET | PG7 | J14 | GPIO | kart algılama |

## Motor/servo çıkışları

| Sinyal | Pin | Top | İşlev | Not |
|---|---|---|---|---|
| OUT1 | PE9 | P9 | TIM1_CH1 | PWM / DShot |
| OUT2 | PE11 | P10 | TIM1_CH2 |  |
| OUT3 | PE13 | N11 | TIM1_CH3 |  |
| OUT4 | PE14 | P11 | TIM1_CH4 |  |
| OUT5 | PD12 | N13 | TIM4_CH1 |  |
| OUT6 | PD13 | M15 | TIM4_CH2 |  |
| OUT7 | PD14 | M14 | TIM4_CH3 |  |
| OUT8 | PD15 | L14 | TIM4_CH4 |  |
| OUT9 | PH10 | L13 | TIM5_CH1 |  |
| OUT10 | PH11 | L12 | TIM5_CH2 |  |
| OUT11 | PH12 | K12 | TIM5_CH3 |  |
| OUT12 | PI0 | E14 | TIM5_CH4 |  |

## Isıl kontrol

| Sinyal | Pin | Top | İşlev | Not |
|---|---|---|---|---|
| PELTIER_PWM_A | PB0 | R5 | TIM3_CH3 | ısıtma yönü |
| PELTIER_PWM_B | PB1 | R4 | TIM3_CH4 | soğutma yönü |

## Zamanlama

| Sinyal | Pin | Top | İşlev | Not |
|---|---|---|---|---|
| PPS_IN | PA15 | A13 | TIM2_CH1 | Operfly Bus PPS girişi (yakalama) |

## Analog ölçüm

| Sinyal | Pin | Top | İşlev | Not |
|---|---|---|---|---|
| V12_BUS_SENS | PA0 | N3 | ADC1_INP16 | omurga gerilimi |
| V5_SENS | PA3 | R2 | ADC1_INP15 |  |
| V3V3_SENS | PA4 | N4 | ADC1_INP18 | sensör beslemesi |
| HW_VER | PF11 | R6 | ADC1_INP2 | kart sürümü direnci |
| HW_REV | PF12 | P6 | ADC1_INP6 | kart revizyonu direnci |

## Güç ve gözetim

| Sinyal | Pin | Top | İşlev | Not |
|---|---|---|---|---|
| SENS1_EN | PG3 | K15 | GPIO | IMU 1 beslemesi |
| SENS2_EN | PG4 | K14 | GPIO | IMU 2 beslemesi |
| SENS3_EN | PG5 | K13 | GPIO | IMU 3 beslemesi |
| WDG_KICK | PH3 | G4 | GPIO | harici watchdog besleme |
| PGOOD_5V | PH6 | M11 | GPIO |  |
| PWR_FAIL_N | PH8 | M12 | GPIO | enerji deposu devrede (kesme) |

## Durum LED

| Sinyal | Pin | Top | İşlev | Not |
|---|---|---|---|---|
| LED_R | PG0 | N7 | GPIO |  |
| LED_G | PG1 | M7 | GPIO |  |
| LED_B | PG2 | L15 | GPIO |  |

## Saat

| Sinyal | Pin | Top | İşlev | Not |
|---|---|---|---|---|
| HSE_IN | PH0 | G1 | RCC_OSC_IN | ana kristal |
| HSE_OUT | PH1 | H1 | RCC_OSC_OUT |  |
| LSE_IN | PC14 | E1 | RCC_OSC32_IN | 32,768 kHz |
| LSE_OUT | PC15 | F1 | RCC_OSC32_OUT |  |

## Boş pinler

PA10, PA8, PB10, PB11, PB14, PB15, PB2, PB4, PB6, PB7, PB8, PB9, PC0, PC13, PC2_C, PC3_C, PD10, PD11, PD5, PD6, PE0, PE1, PE10, PE12, PE15, PE7, PE8, PF10, PF13, PF2, PF3, PF4, PF5, PG10, PG9, PH13, PH14, PH15, PH2, PH7, PH9, PI11, PI7
