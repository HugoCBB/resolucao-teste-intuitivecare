<script>
    import { ref } from 'vue';
    const user = ref({name:"hugo"})

</script>
<template>
    <h1>
        {{ user.name }}
    </h1>
</template>