<template>
    <div v-html="content" />
</template>

<script>
export default {
    props: {
        src: {
            type: String,
            required: true,
        }
    },
    data() {
        return { content: '' };
    },
    watch: {
        src: {
            immediate: true,
            async handler(src) {
                await fetch(src, { headers: { 'Cache-Control': 'no-cache' } })
                    .then(response => response.text())
                    .then(content => this.content = content)
            },
        },
    },
}
</script>