# Remora

The full documentation is at <https://remora-docs.readthedocs.io/en/latest/>
Note: Docs have not been updated for 1.0.0_rc

Remora is a free, opensource LinuxCNC component and Programmable Realtime Unit (PRU) firmware to allow LPC176x and STM32F4 based controller boards to be used in conjuction with a Raspberry Pi to implement a LinuxCNC based CNC controller.

#实验项目所需

个人的实验项目是一个多轴的3D打印机的项目，对于市面上的方案如GRBL性能一般且扩展性较差，转而采用LinuxCNC的方案，LinuxCNC天然支持九轴和自定义运动组件如路径等插补。

传统LinuxCNC的方案采用Mesa的桌面板卡，价格昂贵且国内购买不易，直到在Linuxcnc的论坛上遇到Scotta，经过前期邮件交流和后期论坛交流，确定该方案。
 
 
 -支持传统的打印机组件（采用的是Bigtreetech的打印机主板），适合多轴控制
 -契合LinuxCNC的配置方式，在此基础上配置插补算法
 -成本低廉，采购方便
 

