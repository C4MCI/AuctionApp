import { writable } from "svelte/store";
import CryptoJS from 'crypto-js';

export const store = writable({
    logged_in: false,
    key: '70257dd3f45376884ea7a3b03cc6919a',
    username: '',
    userId: '',
  })
export const lastMsgs = writable([])