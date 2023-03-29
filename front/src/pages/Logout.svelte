<script>
    import {store} from '../Store'
    import { navigate } from 'svelte-navigator';
    import { onMount } from "svelte"

    $store.logged_in = false
    $store.username = ''
    let savestore = true
    $: if (savestore && $store) {
        window.sessionStorage.setItem("store", JSON.stringify($store))
    }
    onMount(async () => {
        let ses = window.sessionStorage.getItem("store")
        if (ses) {
            console.log("sob-- ~ loading ses", ses)
            $store = JSON.parse(ses)
        }
        savestore = true
    })
    
    navigate('/')
</script>