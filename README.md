# ActorCloud



##  Introduction

**ActorCloud** is an IoT platform that provides one-stop platform services for enterprises with low-power IoT networks. **ActorCloud** provides multiple protocol access, message flow management, data parsing and data processing capabilities for devices on a secure and reliable basis.

The platform provides basic device management functions to connect and manage massive devices, realize message communication and data collection persistence of devices, integrate rule engine and data visualization management, flexibly open multiple privilege level management and control API,  quickly develop upper layers through API, and achieve multi-end access and device remote control.

- Multi-protocol access: Support low-power standard protocols such as MQTT, CoAP, LoRaWAN and Websocket, and adapts to mainstream Wi-Fi modules, NB-IoT modules, LoRa gateways and various industrial gateways in the  low-power scenarios;
- Device management: Terminal registration opening and life cycle management, providing continuous monitoring of status, faults, and reported data;
- Data parsing: No need to change the data reporting format of the device, and support writing decoding plug-in for parsing in the cloud;
- Rule Engine: Based on Pulsar, built-in flexible SQL expressions and rich processing functions, realize the real-time parsing of terminal messages, high-speed persistence, rule processing and different types of action triggering;
- Application enablement: Open rich REST API interface, with flexible and configurable application permissions, help enterprises quickly build various upper-layer applications;
- Tenant management: Support multi-tenancy, and the data between tenants is completely isolated. Users in the tenant can be configured with different permissions and management domains.



## Online Demo & Installation

- Visit [https://demo.actorcloud.io](https://demo.actorcloud.io/) to try out the full functionality of **ActorCloud** online.
- Visit [Actorcloud Deployment Documentation](https://docs.actorcloud.io/installation/base.html) to deploy ActorCloud locally for use.



## Getting Started

See the [Quick Start](https://demo.actorcloud.io/getting_started/quick_start.html) document for the basic use of ActorCloud



## Device Access

### Device Quick Access Guide
For the steps of Accessing Devices to ActorCloud, please see the [Device quick access guide](https://demo.actorcloud.io/getting_started/access_guide.html).

### Device Access Method

Although the device messages in any access mode under the same account are interoperable, you need to select the appropriate access method according to the product requirements.

The use of SSL/TLS generally results in higher security while reducing connection performance. Some devices are limited in performance and can only run lightweight CoAP clients, while WebSockets are recommended for real-time communication on the browser.

##### Attached:  Access protocol supported by ActorCloud

| Name                             | Access address                 | Description                              |
| -------------------------------- | ------------------------------ | ---------------------------------------- |
| MQTT                             | broker.actorcloud.io:1883      | Normal MQTT access                       |
| MQTT/SSL                         | broker.actorcloud.io:8883      | SSL MQTT Access (one-way authentication) |
| MQTT/SSL                         | broker.actorcloud.io:8884      | SSL MQTT Access (two-way authentication) |
| CoAP(LwM2M)                      | broker.actorcloud.io:5683/mqtt | CoAP/LwM2M Access                        |
| CoAP(LwM2M)/DTLS                 | broker.actorcloud.io:5684/mqtt | DTLS CoAP/LwM2M Access                   |
| MQTT/WebSocket                   | broker.actorcloud.io:8083/mqtt | WebSocket Access                         |
| MQTT/WebSocket/SSL               | broker.actorcloud.io:8084/mqtt | SSL WebSocket Access                     |
| Private TCP transparent protocol | custom made                    | Private TCP transparent protocol         |



## License

ActorCloud is released under [Apache 2.0 License](https://github.com/actorcloud/ActorCloud/blob/master/LICENSE).