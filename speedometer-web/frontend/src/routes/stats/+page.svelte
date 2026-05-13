<script lang="ts">
	import { onMount } from 'svelte';
	import { fetchStatsSummary } from '$lib/api';

	let stats: any = null;
	let loading = true;

	onMount(async () => {
		try {
			stats = await fetchStatsSummary();
		} catch (e) {
			console.error(e);
		} finally {
			loading = false;
		}
	});
</script>

<div class="container">
	<h1 style="margin-bottom: 2rem;">Statistics</h1>

	{#if loading}
		<p>Loading stats...</p>
	{:else if stats}
		<div class="stats-grid">
			<div class="card stat-card full-width">
				<div class="stat-label">ALL TIME</div>
				<div class="stat-value digital-font">{(stats.all_time_km ?? stats.total_km).toFixed(1)} <span class="unit">km</span></div>
			</div>
			
			<div class="card stat-card">
				<div class="stat-label">TODAY</div>
				<div class="stat-value digital-font">{stats.today_km.toFixed(1)} <span class="unit">km</span></div>
			</div>
			
			<div class="card stat-card">
				<div class="stat-label">THIS WEEK</div>
				<div class="stat-value digital-font">{stats.week_km.toFixed(1)} <span class="unit">km</span></div>
			</div>

			<div class="card stat-card full-width">
				<div class="stat-label">THIS MONTH</div>
				<div class="stat-value digital-font">{stats.month_km.toFixed(1)} <span class="unit">km</span></div>
			</div>
			
			<div class="card stat-card full-width">
				<div class="stat-label">TOTAL TRIPS</div>
				<div class="stat-value digital-font">{stats.trip_count}</div>
			</div>
		</div>
	{:else}
		<p>Failed to load statistics.</p>
	{/if}
</div>

<style>
	.stats-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1rem;
	}

	.stat-card {
		text-align: center;
		padding: 2rem 1rem;
	}

	.full-width {
		grid-column: 1 / -1;
	}

	.stat-label {
		font-size: 0.9rem;
		color: var(--text-secondary);
		margin-bottom: 0.5rem;
		text-transform: uppercase;
	}

	.stat-value {
		font-size: 2.5rem;
		color: var(--accent-color);
	}

	.unit {
		font-size: 1rem;
		color: var(--text-secondary);
	}
</style>
