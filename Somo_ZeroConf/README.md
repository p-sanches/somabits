# SOMA Server
SOMA Server is a server-side application which can automatically discover all the SOMA devices in a network. After discovering it can route sensors and actuators to respective devices based on the user-supplied routing information.

## Usage

Press the Discover button to discover all the SOMA devices in a network.
![picture](interface1.png)

Click on the name of the device to check the attached sensors and actuators 
![picture](interface2.png)

## For Developers
SOMA Server is developed on top of Visual Studio 2017 using .Net Framework.
 
SOMA Server uses Mono.Zeroconf for the discovery of devices which is a Zero Configuration Networking library for .NET
The easiest way to get started is to use the NuGet package.

> Install-Package [Zeroconf](http://www.nuget.org/packages/Zeroconf)


More detailed documentation will come shortly