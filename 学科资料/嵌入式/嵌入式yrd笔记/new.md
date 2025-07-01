NRST低电平触发系统复位

无上下拉模式可以通过外部电阻变成上下拉模式
在硬件上添加一个外部下拉电阻（通常为 10kΩ）到 GND，使引脚在无输入时保持低电平。
在硬件上添加一个外部上拉电阻（通常为 10kΩ）到 VCC，使引脚在无输入时保持高电平。

UART称作为异步串行通信，USART称为同步/异步串行通信，两者都在STM32内部
SPI为串行同步通信
串口通信为逐位传输，有单工(数据单向传输)，半双工(双向传输但不能同时进行)，双工(双向同时传输)三种传输模式
TX发送，RX接收，一般设置PA为TX接口，PA10为RX接口
查询方式：
```c++
void MX_USART1_UART_Init(void){
	// 配置UART1实例，使用USART1硬件
	huart1.Instance = USART1;
	// 设置通信波特率为9600bps，决定数据传输速率
	huart1.Init.BaudRate = 9600;
	// 配置数据位长度为8位，标准数据传输格式
	huart1.Init.WordLength = UART_WORDLENGTH_8B;
	// 设置停止位为1位，用于标识数据帧结束
	huart1.Init.StopBits = UART_STOPBITS_1;
	// 不使用奇偶校验位，降低传输开销但无错误检测
	huart1.Init.Parity = UART_PARITY_NONE;
	// 配置为全双工模式，支持同时发送和接收数据
	huart1.Init.Mode = UART_MODE_TX_RX;
	// 不使用硬件流控制，简化连接但需软件确保数据处理能力
	huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
	// 设置过采样率为16，提高接收数据的准确性和抗干扰能力
	huart1.Init.OverSampling = UART_OVERSAMPLING_16;
	// 调用HAL库初始化UART外设
	// 若初始化失败（返回值不等于HAL_OK），则跳转到错误处理函数
	if (HAL_UART_Init(&huart1) != HAL_OK)
	    Error_Handler();
}


/* Initialize all configured peripherals*/
MX_GPIO Init();
MX_USART1_UART_Init();
/* USER CODE BEGIN 2 */
//发送缓冲区写入数据
memcpy(txbuf,"Hello 2021\r\n",30);
//串口发送缓冲区数据
HAL_UART_Transmit(&huart1,txbuf,strlen((char *)txbuf), 1000);
/*USER CODE END 2 */
/* Infinite loop */
/*USER CODE BEGIN WHILE */
while (1){
/* USER CODE END WHILE *
/* USER CODE BEGIN 3 */
if((HAL_UART_Receive(&huart1 (uint8_t*)&rxdata,1,1000))==HAL_OK)//读取接收数据到接收存储器
   HAL_UART_Transmit(&huart1,(uint8_t*)&rxdata,1,1000);//发送接收存储器中的数据
}
/* USER CODE END 3 */
```


定时器
系统时钟为72MHz，预分频器（PSC）设为7199，计数时钟频率(1s内的计数次数) = 系统时钟 / (PSC + 1)
自动重装载值（ARR）为定时周期，定时时间 = (ARR+1) / 计数时间频率
向上计数：从 0 开始，每次 + 1，直到达到 ARR 值。
向下计数：从 ARR 开始，每次 - 1，直到归零。
中心对齐：先向上计数，再向下计数，形成对称波形。

向上计数模式下：计数器归零，触发更新事件。
向下计数模式下：计数器重置为 ARR，触发更新事件。

```c++
// 初始化配置
TIM_HandleTypeDef htim2;
htim2.Instance = TIM2;
htim2.Init.Prescaler = 7200 - 1;       // 分频系数7200
htim2.Init.CounterMode = TIM_COUNTERMODE_UP;  //向上计数
htim2.Init.Period = 1000 - 1;          // 自动重装载值1000
htim2.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_ENABLE;
HAL_TIM_Base_Init(&htim2);

// 启动定时器（中断方式）
HAL_TIM_Base_Start_IT(&htim2);

// 中断回调函数
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim2) {
	if (htim->Instance == TIM2) {
		HAL_GPIO_TogglePin(GPIOB, GPIO_PIN_0);  // 翻转LED引脚
	}
}


//查询
if(_HAL_TIM_GET_FLAG(&htim2,TIM_FLAG_UPDATE))
{
//控制LED接口翻转
HAL_GPIO_TogglePin(GPIOB.GPIO_PIN_0);
//清除中断标志位
_HAL_TIM_CLEAR_FLAG(&htim2,TIM_FLAG_UPDATE);
}
```

