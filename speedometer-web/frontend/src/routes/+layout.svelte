<script lang="ts">
	import '../app.css';
	import { page } from '$app/stores';
</script>

<main>
	<slot />
</main>

<nav>
	<a href="/" class:active={$page.url.pathname === '/'}>
		<span class="nav-icon">⏱️</span>
		<span>Live</span>
	</a>
	<a href="/trips" class:active={$page.url.pathname.startsWith('/history') || $page.url.pathname.startsWith('/trips')}>
		<span class="nav-icon">📜</span>
		<span>History</span>
	</a>
	<a href="/stats" class:active={$page.url.pathname === '/stats'}>
		<span class="nav-icon">📊</span>
		<span>Stats</span>
	</a>
	<a href="/settings" class:active={$page.url.pathname === '/settings'}>
		<span class="nav-icon">⚙️</span>
		<span>Settings</span>
	</a>
</nav>
