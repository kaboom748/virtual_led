import esphome.codegen as cg
from esphome.components import light, socket
import esphome.config_validation as cv
from esphome.const import (
    CONF_IS_RGBW,
    CONF_MAX_REFRESH_RATE,
    CONF_NUM_LEDS,
    CONF_OUTPUT_ID,
    CONF_PORT,
)

CODEOWNERS = ["@kaboom748"]
AUTO_LOAD = ["socket"]
DEPENDENCIES = ["network"]

ns = cg.esphome_ns.namespace("virtual_led_strip")
VirtualLedStrip = ns.class_("VirtualLedStrip", light.AddressableLight, cg.Component)

CONFIG_SCHEMA = cv.All(
    light.ADDRESSABLE_LIGHT_SCHEMA.extend(
        {
            cv.GenerateID(CONF_OUTPUT_ID): cv.declare_id(VirtualLedStrip),
            cv.Required(CONF_NUM_LEDS): cv.positive_not_null_int,
            cv.Optional(CONF_PORT, default=8083): cv.port,
            cv.Optional(CONF_IS_RGBW, default=False): cv.boolean,
            # Meme semantique qu'esp32_rmt_led_strip: un SEUIL, pas une cadence.
            # LightState::loop() le quantifie a 16 ms -> 32ms donne 31,2 img/s,
            # 33ms en donne 20,9. Seuls les multiples de 16 tombent juste.
            cv.Optional(CONF_MAX_REFRESH_RATE): cv.positive_time_period_microseconds,
        }
    ).extend(cv.COMPONENT_SCHEMA),
    # Sans ca, ESPHome dimensionne lwIP sans nous compter: le ruban de trop
    # echouerait a l'execution au lieu d'etre refuse a la compilation.
    socket.consume_sockets(2, "virtual_led_strip"),
    socket.consume_sockets(1, "virtual_led_strip", socket.SocketType.TCP_LISTEN),
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_OUTPUT_ID])
    await light.register_light(var, config)
    await cg.register_component(var, config)
    cg.add(var.set_num_leds(config[CONF_NUM_LEDS]))
    cg.add(var.set_port(config[CONF_PORT]))
    cg.add(var.set_rgbw(config[CONF_IS_RGBW]))
    if CONF_MAX_REFRESH_RATE in config:
        cg.add(var.set_max_refresh_rate(config[CONF_MAX_REFRESH_RATE]))
