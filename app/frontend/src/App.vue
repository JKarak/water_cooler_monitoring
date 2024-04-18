<template>
    <main class="app">
        <section class="header">
            <h1 class="title">{{ title }}</h1>
        </section>
        <section class="main">
            <div v-if="isSensorsLoading">
                <p>Загрузка информации о датчиках...</p>
            </div>
            <div v-else>
                <section class="sensors">
                    <section class="sensors-map-panel">
                        <svg-img :src="svgMap" ref="sensors_map" class="sensors-map" />
                    </section>
                    <section class="sensors-text-panel">
                        <div class="sensors-list">
                            <div v-for="sensor in sensors" :key="sensor.id" :id="sensor.id" class="sensor-item">
                                {{ sensor.id }}: status={{ sensor.state.status }}, liquid={{ sensor.state.liquid }}
                            </div>
                        </div>
                    </section>
                </section>
            </div>
        </section>
    </main>
</template>

<script>
import SvgImg from '@/components/global/SvgImg.vue';

const baseUrl = `http://${window.location.hostname}:8000`;
const sensorsSseUrl = `${baseUrl}/sse/sensors`;
const sensorsMapUrl = `${baseUrl}/sensors/map`;
const sensorsListUrl = `${baseUrl}/sensors/list`;

export default {
    name: 'App',
    components: {
        SvgImg: SvgImg
    },
    data: function () {
        return {
            title: 'Контроль наличия воды в кулерах',
            svgMap: sensorsMapUrl,
            sensors: {},
            isSensorsLoading: false,
        }
    },
    mounted() {
        this.$nextTick(function () {
            // Код, который будет запущен только после отрисовки всех представлений
            this.setupSensors();
        })
    },
    methods: {
        setupStream() {
            let evtSource = new EventSource(sensorsSseUrl)

            evtSource.addEventListener('open', event => {
                console.log("Connected to the SSE.");
                console.log(event);
            }, false);

            evtSource.addEventListener('message', event => {
                const data = JSON.parse(event.data);
                console.log(data);

                if (Object.getOwnPropertyDescriptor(data, "sensors")) {
                    this.sensors = data.sensors;
                    return;
                }

                if (Object.getOwnPropertyDescriptor(data, "sensor")) {
                    if (data.sensor in this.sensors) {
                        let sensor = this.sensors[data.sensor];
                        if (!("state" in sensor)) {
                            sensor["state"] = {};
                        }

                        for (const stateName in data.state) {
                            const stateValue = data.state[stateName];
                            sensor["state"][stateName] = stateValue;
                            this.updateSensorStateOnMap(data.sensor, stateName, stateValue);
                        }
                    }
                    return;
                }
            }, false);

            evtSource.addEventListener('error', event => {
                if (event.readyState == EventSource.CLOSED) {
                    console.log('Event was closed.');
                    console.log(event);
                }
            }, false);
        },
        async getSensors() {
            this.isSensorsLoading = true;
            await fetch(sensorsListUrl)
                .then(response => response.json())
                .then(data => {
                    this.sensors = data;
                    this.isSensorsLoading = false;
                });
        },
        setupSensors() {
            try {
                this.getSensors();
            } catch (error) {
                console.log(error);
            }
        },
        updateSensorStateOnMap(sensorId, stateName, stateValue) {
            const svg = this.$refs.sensors_map.$el.firstElementChild;
            const sensorsGroup = svg.querySelector("g[inkscape\\:label='sensors']")
            const sensorGroup = sensorsGroup.querySelector(`g[inkscape\\:label='${sensorId}']`);

            if (stateName === 'status') {
                switch (stateValue) {
                    case 'down':
                        sensorGroup.querySelector("g[inkscape\\:label='down']").setAttribute('style', 'display:inline');
                        sensorGroup.querySelector("g[inkscape\\:label='up']").setAttribute('style', 'display:none');
                        break;
                    case 'up':
                        sensorGroup.querySelector("g[inkscape\\:label='down']").setAttribute('style', 'display:none');
                        sensorGroup.querySelector("g[inkscape\\:label='up']").setAttribute('style', 'display:inline');
                        break;
                }
                return;
            }

            if (stateName === 'liquid') {
                sensorGroup.querySelector("g[inkscape\\:label='down']").setAttribute('style', 'display:none');
                const state_up_group = sensorGroup.querySelector("g[inkscape\\:label='up']")
                state_up_group.setAttribute('style', 'display:inline');

                switch (stateValue) {
                    case '0':
                        state_up_group.querySelector("g[inkscape\\:label='empty']").setAttribute('style', 'display:inline');
                        state_up_group.querySelector("g[inkscape\\:label='not_empty']").setAttribute('style', 'display:none');
                        break;
                    case '1':
                        state_up_group.querySelector("g[inkscape\\:label='empty']").setAttribute('style', 'display:none');
                        state_up_group.querySelector("g[inkscape\\:label='not_empty']").setAttribute('style', 'display:inline');
                        break;
                }
                return;
            }
        },
    },
    created: function () {
        this.setupStream();
    }
}
</script>

<style>
body {
    margin: 0;
    padding: 0;
    height: 100vh;
}

h1 {
    font-size: 2.5em;
}

#app {
    font-family: Avenir, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: center;
    color: #2c3e50;
    height: 100vh;
}

.sensors {
    display: flex;
    height: 100%;
    padding: 15px;
    gap: 20px;
}

.sensors-map-panel {
    flex-grow: 1;
    flex-basis: 70%;
    text-align: right;
    height: 80vh;
}

.sensors-text-panel {
    flex-shrink: 2;
    flex-basis: 30%;
    text-align: left;
}

.sensors-map,
.sensors-map>svg {
    height: 100%;
    width: auto;
}
</style>
