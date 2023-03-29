<script>
  import Navbar from "./Navbar.svelte";
  import { navigate } from "svelte-routing";
  import axios from "axios";
  import CryptoJS from "crypto-js";
  import { store } from "../Store";
  import { onMount } from "svelte";

  let id = "";
  let username = "";
  let email = "";
  let password = "";

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

  async function handleSubmit(event) {
    event.preventDefault();

    if (username === "" || email === "" || password === "") {
      alert("Please fill in all fields");
    } else {
      let encryptedPassword = CryptoJS.HmacSHA256(
        password,
        $store.key
      ).toString();

      const data = { id, username, email, password: encryptedPassword };

      try {
        const response = await axios.post(
          `http://localhost:8000/register`,
          data
        );
        alert("Registration succesful! Please log in.");
        username = "";
        email = "";
        password = "";
        navigate("/login");
      } catch (e) {
        alert(`Registration failed: ${e.response.data.detail}`);
      }
    }
  }
</script>

<Navbar />

<form on:submit={handleSubmit}>
  <label for="username">Username</label>
  <input type="text" id="username" bind:value={username} required />

  <label for="email">Email</label>
  <input type="email" id="email" bind:value={email} required />

  <label for="password">Password</label>
  <input type="password" id="password" bind:value={password} required />

  <button type="submit">Register</button>
</form>

<style>
  form {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin-top: 50px;
  }

  label {
    font-size: 18px;
    margin-top: 20px;
  }

  input {
    width: 300px;
    height: 40px;
    font-size: 16px;
    padding: 5px;
    margin-top: 10px;
  }

  button {
    width: 100px;
    height: 40px;
    background-color: #7a709e;
    color: white;
    font-size: 18px;
    border: none;
    border-radius: 5px;
    margin-top: 15px;
    cursor: pointer;
  }

  button:hover {
    background-color: #827c97;
  }
</style>
