# Forwards serial data unmodified (or if valid as JSON) to UDP

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

Parse JSON example

```gdscript

func _process(delta: float) -> void:
	serial_server.poll()
	if serial_server.is_connection_available():
		var packet := serial_server.take_connection().get_packet()
		var json_string = packet.get_string_from_utf8()
		print("Received data: %s" % json_string)
		
		var json = JSON.new()
		var error = json.parse(json_string)
		if error == OK:
			var data_received = json.data
			if data_received.has("data"):
				var d = data_received["data"]
				print(d)
		else:
			print("JSON Parse Error: ", json.get_error_message(), " in ", json_string, " at line ", json.get_error_line())
```
------

TODO

* [ ] Add support for non line terminated serial data
* [ ] Add support for custom UDP ports
* [ ] Add support for custom IP addresses
* [ ] Add support for custom baud rates
