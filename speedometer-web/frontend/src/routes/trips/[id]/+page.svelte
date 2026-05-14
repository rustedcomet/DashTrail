<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { fetchTrip, deleteTrip } from '$lib/api';
	import { goto } from '$app/navigation';
	import Map from '$lib/Map.svelte';
	import { formatDate, formatTime } from '$lib/time';

	let trip: any = null;
	let loading = true;
	let mapPoints: [number, number][] = [];

	onMount(async () => {
		try {
			trip = await fetchTrip(Number($page.params.id));
			if (trip.route_points) {
				mapPoints = trip.route_points.map((p: any) => [p.lat, p.lng]);
			}
		} catch (e) {
			console.error(e);
			alert('Trip not found or error loading.');
			goto('/trips');
		} finally {
			loading = false;
		}
	});

	function formatDuration(seconds: number) {
		const h = Math.floor(seconds / 3600);
		const m = Math.floor((seconds % 3600) / 60);
		const s = Math.floor(seconds % 60);
		return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
	}

	function formatCoords(lat: number | null, lng: number | null) {
		if (lat === null || lat === undefined || lng === null || lng === undefined) return 'Unavailable';
		return `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
	}

	function formatLocation(address: string | null, lat: number | null, lng: number | null) {
		return address || formatCoords(lat, lng);
	}

	async function handleDelete() {
		if (confirm('Are you sure you want to delete this trip?')) {
			try {
				await deleteTrip(trip.id);
				goto('/trips');
			} catch (e) {
				alert('Failed to delete trip.');
			}
		}
	}
</script>

<div class="container">
	<div class="header-row">
		<a href="/trips" class="back-link">Back</a>
		{#if !loading && trip}
			<button class="btn btn-danger delete-btn" on:click={handleDelete}>Delete</button>
		{/if}
	</div>

	{#if loading}
		<p>Loading trip details...</p>
	{:else if trip}
		<div class="card summary-card">
			<h2>Trip Summary</h2>
			<div class="trip-meta">
				<p><strong>Date:</strong> {formatDate(trip.started_at)}</p>
				<p><strong>Start:</strong> {formatTime(trip.started_at)}</p>
				<p><strong>End:</strong> {trip.ended_at ? formatTime(trip.ended_at) : 'In progress'}</p>
				<p><strong>Start location:</strong> {formatLocation(trip.start_address, trip.start_lat, trip.start_lng)}</p>
				<p><strong>Stop location:</strong> {formatLocation(trip.end_address, trip.end_lat, trip.end_lng)}</p>
			</div>

			<div class="stats-grid">
				<div class="stat-card">
					<div class="stat-label">DIST</div>
					<div class="stat-value digital-font">{trip.distance_km.toFixed(2)}</div>
					<div class="unit">km</div>
				</div>
				<div class="stat-card">
					<div class="stat-label">TIME</div>
					<div class="stat-value digital-font duration-value">{formatDuration(trip.duration_seconds)}</div>
					<div class="unit">h:m:s</div>
				</div>
				<div class="stat-card">
					<div class="stat-label">AVG</div>
					<div class="stat-value digital-font">{trip.avg_speed_kmh.toFixed(1)}</div>
					<div class="unit">km/h</div>
				</div>
				<div class="stat-card">
					<div class="stat-label">MAX</div>
					<div class="stat-value digital-font">{trip.max_speed_kmh.toFixed(1)}</div>
					<div class="unit">km/h</div>
				</div>
			</div>
		</div>

		<div class="card map-card">
			<h2>Route Map</h2>
			<div class="map-container">
				{#if mapPoints.length > 0}
					<Map points={mapPoints} />
				{:else}
					<p class="empty-map">No GPS points recorded for this trip.</p>
				{/if}
			</div>
		</div>
	{/if}
</div>

<style>
	.header-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 1.5rem;
	}

	.back-link {
		color: var(--accent-color);
		text-decoration: none;
		font-weight: bold;
	}

	.delete-btn {
		padding: 0.5rem 1rem;
		font-size: 1rem;
	}

	.summary-card {
		margin-bottom: 2rem;
	}

	.summary-card h2,
	.map-card h2 {
		margin-bottom: 1rem;
	}

	.trip-meta {
		margin-bottom: 1.5rem;
		color: var(--text-secondary);
		line-height: 1.6;
	}

	.stats-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 1rem;
	}

	@media (min-width: 600px) {
		.stats-grid {
			grid-template-columns: repeat(4, 1fr);
		}
	}

	.stat-card {
		background-color: #252525;
		padding: 1rem;
		border-radius: 8px;
		text-align: center;
	}

	.stat-label {
		font-size: 0.8rem;
		color: var(--text-secondary);
		margin-bottom: 0.25rem;
	}

	.stat-value {
		font-size: 1.5rem;
		color: var(--text-primary);
	}

	.duration-value {
		font-size: 1.1rem;
	}

	.unit {
		font-size: 0.8rem;
		color: var(--text-secondary);
	}

	.map-card {
		padding: 1rem;
	}

	.map-container {
		width: 100%;
		height: 400px;
		background-color: #252525;
		border-radius: 8px;
		overflow: hidden;
	}

	.empty-map {
		text-align: center;
		padding: 2rem;
	}
</style>
