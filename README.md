# Forwards serial data unmodified to UDP

Developed to use microcontrollers with godot engine without relying on custom native modules.

Godot implementation

```gdscript

var serial_server := UDPServer.new()

func _ready():
    var port: int = 5005
    print("listen for serial data on port ", port)
    serial_server.listen(port, "127.0.0.1")


func _process(delta: float) -> void:
    serial_server.poll()
    if serial_server.is_connection_available():
        var packet := serial_server.take_connection().get_packet()
        print("Received data: %s" % packet.get_string_from_utf8())
```

------

TODO

* [ ] Add support for non line terminated serial data
* [ ] Add support for custom UDP ports
* [ ] Add support for custom IP addresses
* [ ] Add support for custom baud rates
