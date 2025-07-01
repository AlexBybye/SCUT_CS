在STM32微控制器中，GPIO（通用输入输出）引脚的工作模式有多种。根据你给出的代码`GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;`，可知这是在配置GPIO为复用推挽模式。下面为你介绍STM32中GPIO的其他工作模式：

1. **输入模式**
   - `GPIO_MODE_INPUT`：普通输入模式，用于读取外部信号。
   - `GPIO_MODE_IT_RISING`：上升沿触发的中断输入模式。
   - `GPIO_MODE_IT_FALLING`：下降沿触发的中断输入模式。
   - `GPIO_MODE_IT_RISING_FALLING`：边沿触发的中断输入模式，上升沿和下降沿都能触发。
   - `GPIO_MODE_EVT_RISING`：上升沿触发的事件输入模式。
   - `GPIO_MODE_EVT_FALLING`：下降沿触发的事件输入模式。
   - `GPIO_MODE_EVT_RISING_FALLING`：边沿触发的事件输入模式。

2. **输出模式**
   - `GPIO_MODE_OUTPUT_PP`：推挽输出模式，能输出高低电平，适用于连接数字器件。
   - `GPIO_MODE_OUTPUT_OD`：开漏输出模式，需要外接上拉电阻才能输出高电平，常用于I2C等通信总线。

1. **复用功能模式** “复用”（Alternate Function，AF）指的是 GPIO 引脚除了作为普通的输入或输出端口使用外，还能被配置为特定外设功能的引脚。
   - `GPIO_MODE_AF_PP`：复用推挽模式，用于复用功能，比如USART的TX、RX引脚。
   - `GPIO_MODE_AF_OD`：复用开漏模式，同样用于复用功能，像I2C的SDA、SCL引脚。

4. **模拟模式**
   - `GPIO_MODE_ANALOG`：模拟模式，用于ADC（模拟-to-数字转换）或DAC（数字-to-模拟转换）功能，此时GPIO不参与数字信号的输入输出。

选择不同的GPIO模式要依据具体的应用场景。比如，若要读取按键状态，可选用`GPIO_MODE_INPUT`；若要驱动LED，可选用`GPIO_MODE_OUTPUT_PP`；若要使用SPI、USART等外设，则需选用复用功能模式。