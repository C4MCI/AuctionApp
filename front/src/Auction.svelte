<script>
    import axios from "axios";
    import { navigate } from "svelte-navigator";
    import { lastMsgs } from "./Store";
    import { useParams } from "svelte-navigator";
    import Navbar from "./pages/Navbar.svelte";
    import { store } from "./Store";

    if (!$store.logged_in) {
        alert("Please log in to see this page.");
        navigate("/login");
    }

    const params = useParams();

    $: item = getItem();
    let id = $params.id;
    $: currentBid = 0;
    let isFinished = false;
    const user = $store.username;
    const participant = $store.userId;
    let auctionEnds;
    $: newBid = getMinBid(item, currentBid);
    $: countdown = (auctionEnds - new Date()) / 1000;
    let interval;

    const getMinBid = (item, currentBid) => {
        return item.then(
            (i) =>
                (newBid = currentBid
                    ? Math.max(i.item.min_price, currentBid) + i.item.price_step
                    : Math.max(i.item.min_price, currentBid))
        );
    };

    async function getItem() {
        try {
            const response = await axios.get(
                `http://localhost:8000/auction/${id}`
            );
            currentBid = response.data.item.bid;
            return await response.data;
        } catch (e) {
            alert(
                "Please be sure that you are running from port 5173. If not, you should allow your port from main.py line 23"
            );
        }
    }

    function isJsonString(str) {
        try {
            JSON.parse(str);
        } catch (e) {
            return false;
        }
        return true;
    }

    const ws = new WebSocket(
        `ws://localhost:8000/auction/${id}/ws/${participant}`
    );

    ws.onmessage = (event) => {
        let incoming = event.data;
        if (isJsonString(incoming)) {
            incoming = JSON.parse(incoming);
            if (incoming.new_price) {
                currentBid = incoming.new_price;
                let ends = incoming.ends.slice(1, -1);
                auctionEnds = new Date(ends);
                clearInterval(interval);
                interval = setInterval(() => {
                    countDown();
                }, 1000);
            } else if (incoming.json_data.completed) {
                isFinished = incoming.json_data.completed;
            }
        } else {
            $lastMsgs = [...$lastMsgs, incoming];
        }
    };

    const makeNewBid = (e) => {
        const data = JSON.stringify({ bid: newBid });
        ws.send(data);
        e.preventDefault();
    };

    const countDown = () => {
        if (countdown > 0) {
            countdown -= 1;
        } else {
            clearInterval(interval);
            countdown = 0;
            isFinished = true;
        }
    };
</script>

<main>
    <Navbar />
    <div>
        <hr />
    </div>
    <div class="grid">
        <div class="container">
            {#await item}
                <p>Loading info...</p>
            {:then item}
                <img src={item.item.url} alt="painting" />
                <p>{item.item.item_name}</p>
                <p class="description">{item.item.item_description}</p>

                {#if !currentBid}
                    <p>
                        The starting price is <span class="price"
                            >${item.item.min_price}</span
                        >
                    </p>
                {:else}
                    <p>
                        {#if !isFinished}Current bid is
                        {:else}
                            The last bid was
                        {/if} <span class="price">${currentBid}</span>
                    </p>
                {/if}

                {#if !isNaN(auctionEnds)}
                    {#if countdown > 0}
                        <p>Auction ending in {countdown.toFixed(0)} secs!</p>
                        <progress
                            id="time"
                            value={countdown.toFixed(0)}
                            max="60"
                        />
                        <p />
                    {:else}
                        <p>Auction ended!</p>
                    {/if}
                {/if}

                <button disabled={isFinished} on:click={makeNewBid}>
                    Bid $ {newBid}
                </button>
            {/await}
        </div>
        <div class="announcement">
            <p>Welcome, {user}!</p>
            {#each $lastMsgs as msg}
                <h4>{msg}</h4>
            {/each}
        </div>
    </div>
</main>

<style>
    .container {
        display: left;
        justify-self: center;
        flex-direction: column;
        max-height: 100%;
    }
    .grid {
        display: grid;
        gap: 10px;
        grid-template-columns: auto auto;
        min-height: 600px;
        min-width: 0;
        max-height: fit-content;
    }
    img {
        width: auto;
        max-height: 40%;
        border: solid 2px white;
    }
    .description {
        font-style: italic;
    }

    .price {
        align-items: center;
        color: #ee83e5;
        font-weight: 700;
    }

    .announcement {
        margin: 5px;
        padding: 5px;
        width: 500px;
        height: 400px;
        overflow: auto;
        text-align: justify;
    }
</style>
