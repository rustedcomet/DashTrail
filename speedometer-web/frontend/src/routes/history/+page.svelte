<script lang="ts">
	import { onMount } from 'svelte';
	import { fetchTrips } from '$lib/api';
	import { formatDate, formatTime } from '$lib/time';

	let trips: any[] = [];
	let loading = true;

	onMount(async () => {
		try {
			trips = await fetchTrips();
		} catch (e) {
			console.error(e);
		} finally {
			loading = false;
		}
	});

	function formatDuration(seconds: number) {
		const h = Math.floor(seconds / 3600);
		const m = Math.floor((seconds % 3600) / 60);
		const s = Math.floor(seconds % 60);
		if (h > 0) return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
		return `${m}:${s.toString().padStart(2, '0')}`;
	}
</script>

<div class="container">
	<h1 style="margin-bottom: 2rem;">Trip History</h1>

	{#if loading}
		<p>Loading trips...</p>
	{:else if trips.length === 0}
		<p>No trips recorded yet.</p>
	{:else}
		<div class="trip-list">
			{#each trips as trip}
				<a href="/trips/{trip.id}" class="card trip-card">
					<div class="trip-date">
						{formatDate(trip.started_at)}
						{formatTime(trip.started_at)}
					</div>
					<div class="trip-stats">
						<div>
							<div class="stat-label">DIST</div>
							<div class="stat-val">{trip.distance_km.toFixed(2)} km</div>
						</div>
						<div>
							<div class="stat-label">DUR</div>
							<div class="stat-val">{formatDuration(trip.duration_seconds)}</div>
						</div>
						<div>
							<div class="stat-label">AVG</div>
							<div class="stat-val">{trip.avg_speed_kmh.toFixed(1)} km/h</div>
						</div>
						<div>
							<div class="stat-label">MAX</div>
							<div class="stat-val">{trip.max_speed_kmh.toFixed(1)} km/h</div>
						</div>
					</div>
				</a>
			{/each}
		</div>
	{/if}
</div>

<style>
	.trip-list {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.trip-card {
		text-decoration: none;
		color: var(--text-primary);
		display: block;
		transition: transform 0.1s, background-color 0.2s;
	}

	.trip-card:hover, .trip-card:active {
		transform: scale(0.98);
		background-color: #252525;
	}

	.trip-date {
		font-weight: bold;
		margin-bottom: 1rem;
		border-bottom: 1px solid #333;
		padding-bottom: 0.5rem;
		color: var(--accent-color);
	}

	.trip-stats {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 0.75rem;
	}

	.stat-label {
		font-size: 0.75rem;
		color: var(--text-secondary);
	}

	.stat-val {
		font-weight: bold;
		font-family: 'Orbitron', sans-serif;
	}
</style>
