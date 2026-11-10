import { mount } from 'svelte';
import App from './App.svelte';

const base = document.createElement('base');
base.href = 'https://otodb.net/';
base.target = '_blank';
document.head.append(base);

mount(App, { target: document.getElementById('app')! });
