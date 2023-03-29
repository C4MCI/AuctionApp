<script>
  import { Router, Route, Link } from "svelte-navigator";
  import Auction from "./Auction.svelte";
  import axios from "axios";
  import Navbar from "./pages/Navbar.svelte";
  import { store } from "./Store";
  import Register from "./pages/Register.svelte";
  import Login from "./pages/Login.svelte";
  import Logout from "./pages/Logout.svelte";
  import { onMount } from "svelte";

  function getStores() {
    let ses = window.sessionStorage.getItem("store");
    if (ses) {
      console.log("sob-- ~ loading ses", ses);
      $store = JSON.parse(ses);
    }
  }

  getStores();

  let savestore = false;
  $: if (savestore && $store) {
    window.sessionStorage.setItem("store", JSON.stringify($store));
  }
  onMount(async () => {
    let ses = window.sessionStorage.getItem("store");
    if (ses) {
      console.log("sob-- ~ loading ses", ses);
      $store = JSON.parse(ses);
    }
    savestore = true;
  });

  let auctions = getAuctions();

  async function getAuctions() {
    try {
      const response = await axios.get(`http://localhost:8000/auctions`);
      auctions = response.data;
      return await response.data;
    } catch (e) {
      alert(
        "Please be sure that you are running from port 5173. If not, you should allow your port from main.py line 23"
      );
    }
  }
</script>

<Router>
  <main>
    <Route path="/">
      <Navbar />
      {#if !$store.logged_in}
        <h1>Please Log In to see this page.</h1>
      {:else}
        {#await auctions}
          <p>Loading</p>
        {:then auctions}
          {#each auctions as au}
            <div class="card">
              <div class="card_body">
                <img class="tokenImage" src={au.url} alt="" />
                <h2>Auction {au.id}</h2>
                <p class="description">{au.item_description}</p>
                <div class="info">
                  <div class="price">
                    <p>${au.bid ? au.bid : au.min_price}</p>
                  </div>
                  <div class="duration">
                    {#if au.bid && !au.completed}
                      <p>Ongoing!</p>
                    {:else if !au.bid && !au.completed}
                      <p>Starting Soon!</p>
                    {:else}
                      <p>Finished</p>
                    {/if}
                  </div>
                </div>

                <hr />
                <a class="button" href="/auction/{au.id}">Join Auction</a>
              </div>
            </div>
          {/each}
        {/await}
      {/if}
    </Route>

    <Route path="/auction/:id" component={Auction} />
  </main>

  <Route path="/register">
    <Register />
  </Route>

  <Route path="/login">
    <Login />
  </Route>

  <Route path="/logout">
    <Logout />
  </Route>
</Router>

<style>
  main {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto",
      "Oxygen", "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans",
      "Helvetica Neue", sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    user-select: none;
    min-width: 0;
  }

  .button {
    border-radius: 16px;
    border: 2px solid white;
    padding: 1em 1em;
    font-size: 1em;
    font-weight: 500;
    font-family: inherit;
    align-items: center;
    cursor: pointer;
    transition: border-color 0.25s;
    color: white;
  }
  .button:hover {
    border-color: #646cff;
    color: #646cff;
  }
  .button:focus,
  .button:focus-visible {
    outline: 4px auto -webkit-focus-ring-color;
  }

  .card {
    display: inline-block;
    user-select: none;
    max-width: 300px;
    margin: 1rem 1rem;
    padding: auto;
    border: 1px solid #ffffff22;
    background-color: #282c34;
    background: linear-gradient(
      0deg,
      rgba(40, 44, 52, 1) 0%,
      rgba(17, 0, 32, 0.5) 100%
    );
    box-shadow: 0 7px 20px 5px #00000088;
    border-radius: 0.7rem;
    backdrop-filter: blur(7px);
    -webkit-backdrop-filter: blur(7px);
    overflow: hidden;
    transition: 0.5s all;
  }

  .card_body {
    display: flex;
    flex-direction: column;
    text-align: center;
    width: 90%;
    color: white;
    padding: 1rem;
  }
  .tokenImage {
    border-radius: 0.5rem;
    max-width: 100%;
    height: 250px;
    object-fit: cover;
  }
  .description {
    margin: 0.5rem 0;
    place-content: center;
    color: #a89ec9;
    text-align: center;
  }
  .info {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .price {
    display: flex;
    align-items: center;
    color: #ee83e5;
    font-weight: 700;
  }
  ins {
    margin-left: -0.3rem;
    margin-right: 0.5rem;
  }
  .duration {
    display: flex;
    align-items: center;
    color: #a89ec9;
    margin-right: 0.2rem;
  }
  ins {
    margin: 0.5rem;
    margin-bottom: 0.4rem;
  }
  hr {
    width: 100%;
    border: none;
    border-bottom: 1px solid #88888855;
    margin-top: 0;
  }

  h1 {
    text-align: center;
  }
</style>
