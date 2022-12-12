import eventlet
import json
from flask import Flask, render_template
from flask_mqtt import Mqtt
from flask_socketio import SocketIO, emit
from flask_bootstrap import Bootstrap
from database_helper import DB_helper
from logic import *



eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET'] = 'my secret key'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MQTT_BROKER_URL'] = 'broker.mqttdashboard.com'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = ''
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_KEEPALIVE'] = 30
app.config['MQTT_TLS_ENABLED'] = False
app.config['MQTT_CLEAN_SESSION'] = True


mqtt = Mqtt(app)
async_mode = None
socketio = SocketIO(app)
bootstrap = Bootstrap(app)

#Database, initialize database object and setup it
db_object: DB_helper = DB_helper(db_name='test2.db')
db_object.setup()



@socketio.on('publish')
def handle_publish(json_str):
    data = json.loads(json_str)
    mqtt.publish(data['topic'], data['message'])


@socketio.on('subscribe')
def handle_subscribe(json_str):
    data = json.loads(json_str)
    print("Subscription requested on topic: ")
    mqtt.subscribe(data['topic'])


@socketio.on('unsubscribe_all')
def handle_unsubscribe_all():
    mqtt.unsubscribe_all()

@socketio.event
def my_ping():
    emit('my_pong')

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    print(type(eval(message.payload.decode('utf-8'))))
    print(message.payload.decode('utf-8'))
    data = dict(
        topic=message.topic,
        payload=eval(message.payload.decode('utf-8'))
    )
    robId = data['payload']['deviceId']
    event = data['payload']['state']
    print(robId,'\n', event)
    # Get correct mqtt broker message
    if "ii22/telemetry" in data['topic']:
        # Insert data to databases and emit it to the frontend and update .html view
        db_object.insert_event(robotID=robId, eventype=event)
        socketio.emit('mqtt_message', data=db_object.get_all_events())
    print(data)


@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    print(level, buf)

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('ii22/telemetry/#')


@app.route('/')
def index():
    '''Render the frontend page'''
    return render_template('index.html')

@app.route('/scada')
def scada():
    '''Render the frontend page'''
    return render_template('scada.html')


@app.get("/update")
def update():
    '''Update event history tab view'''
    return get_all_event_data(db_object)
    

@app.get("/update_state")
def update_state():
    '''Show latest robot states'''
    return get_robot_states(db_object)

@app.get("/alarms")
def alarms():
    return  get_alarms_history(db_object)


if __name__ == '__main__':
    # important: Do not use reloader because this will create two Flask instances.
    # Flask-MQTT only supports running with one instance
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False, debug=False)
