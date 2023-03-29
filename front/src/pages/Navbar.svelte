<script>
    import { store } from "../Store";
</script>
<div class="topnav">
    <a class="active" href="/">Auction App</a>
    {#if !$store.logged_in}
        <a href="/register">Register</a>
        <a href="/login">Log In</a>
    {:else}
        <a href="/logout">Log Out</a>  
        <a href="#">{$store.username} #{$store.userId}</a>
    {/if}


  </div>

  <style>
.topnav {
  background-color: #333;
  overflow: hidden;
}

/* Style the links inside the navigation bar */
.topnav a {
  float: right;
  color: #f2f2f2;
  text-align: center;
  padding: 14px 16px;
  text-decoration: none;
  font-size: 17px;
}

/* Change the color of links on hover */
.topnav a:hover {
  background-color: #ddd;
  color: black;
}

/* Add a color to the active/current link */
.topnav a.active {
  float: left;
  background-color: #7a709e;
  color: white;
}

@media (prefers-color-scheme: light) {
    .topnav {
        background-color: #f2f2f2;
    }
    .topnav a {
        color: black;
    }
}
  </style>