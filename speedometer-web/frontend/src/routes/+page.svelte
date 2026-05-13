<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { addTripPoints, createTrip, deleteTrip, stopTrip } from '$lib/api';
	import { calculateDistance, type RoutePoint } from '$lib/gps';
	import { goto } from '$app/navigation';

	let watchId: number | null = null;
	let tripId: number | null = null;
	let isTracking = false;
	let currentSpeed = 0; // km/h
	let maxSpeed = 0; // km/h
	let distance = 0; // km
	let startTime: Date | null = null;
	let routePoints: RoutePoint[] = [];
	let lastPosition: GeolocationPosition | null = null;
	let gpsStatus = 'Offline';
	let elapsedSeconds = 0;
	let timerInterval: ReturnType<typeof setInterval>;
	let wakeLock: any = null;
	let unsyncedPoints: RoutePoint[] = [];
	let syncInFlight = false;

	function formatTime(seconds: number) {
		const h = Math.floor(seconds / 3600);
		const m = Math.floor((seconds % 3600) / 60);
		const s = seconds % 60;
		if (h > 0) return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
		return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
	}

	async function requestWakeLock() {
		try {
			if ('wakeLock' in navigator) {
				wakeLock = await (navigator as any).wakeLock.request('screen');
			}
		} catch {
			wakeLock = null;
		}
	}

	async function releaseWakeLock() {
		if (!wakeLock) return;
		try {
			await wakeLock.release();
		} finally {
			wakeLock = null;
		}
	}

	async function flushPoints(force = false) {
		if (!tripId || unsyncedPoints.length === 0) return;
		if (syncInFlight) {
			if (!force) return;
			while (syncInFlight) {
				await new Promise((resolve) => setTimeout(resolve, 100));
			}
		}

		const batch = [...unsyncedPoints];
		syncInFlight = true;
		try {
			await addTripPoints(tripId, batch);
			unsyncedPoints = unsyncedPoints.slice(batch.length);
		} finally {
			syncInFlight = false;
		}

		if (force && unsyncedPoints.length > 0) {
			await flushPoints(true);
		}
	}

	async function startTracking() {
		if (!navigator.geolocation) {
			alert('Geolocation is not supported by your browser');
			return;
		}

		startTime = new Date();
		gpsStatus = 'Starting...';
		try {
			const created = await createTrip(startTime.toISOString());
			tripId = created.id;
		} catch (err) {
			gpsStatus = 'Offline';
			alert('Failed to start trip: ' + err);
			return;
		}

		isTracking = true;
		routePoints = [];
		unsyncedPoints = [];
		distance = 0;
		maxSpeed = 0;
		currentSpeed = 0;
		elapsedSeconds = 0;
		lastPosition = null;
		gpsStatus = 'Acquiring...';
		await requestWakeLock();

		timerInterval = setInterval(() => {
			if (isTracking) elapsedSeconds++;
		}, 1000);

		watchId = navigator.geolocation.watchPosition(
			(position) => {
				gpsStatus = 'Active';
				processPosition(position);
			},
			(error) => {
				gpsStatus = `Error: ${error.message}`;
			},
			{
				enableHighAccuracy: true,
				maximumAge: 1000,
				timeout: 10000
			}
		);
	}

	async function stopTracking() {
		if (watchId !== null) {
			navigator.geolocation.clearWatch(watchId);
			watchId = null;
		}
		isTracking = false;
		clearInterval(timerInterval);
		await releaseWakeLock();
		gpsStatus = 'Offline';
		currentSpeed = 0;

		if (routePoints.length > 0 && distance > 0.05 && tripId) { // Only save if more than 50m
			const endTime = new Date();
			const durationSeconds = Math.round((endTime.getTime() - startTime!.getTime()) / 1000);
			const avgSpeed = durationSeconds > 0 ? (distance / (durationSeconds / 3600)) : 0;

			const tripData = {
				ended_at: endTime.toISOString(),
				duration_seconds: durationSeconds,
				distance_meters: Number((distance * 1000).toFixed(1)),
				avg_speed_kmh: Number(avgSpeed.toFixed(1)),
				max_speed_kmh: Number(maxSpeed.toFixed(1)),
				end_lat: routePoints[routePoints.length - 1]?.lat,
				end_lng: routePoints[routePoints.length - 1]?.lng
			};

			try {
				await flushPoints(true);
				const saved = await stopTrip(tripId, tripData);
				tripId = null;
				goto(`/trips/${saved.id}`);
			} catch (err) {
				alert('Failed to save trip: ' + err);
			}
		} else {
			if (tripId) {
				await deleteTrip(tripId);
				tripId = null;
			}
			alert('Trip was too short to save.');
		}
	}

	function processPosition(position: GeolocationPosition) {
		const { latitude, longitude, accuracy, speed } = position.coords;

		if (accuracy > 50) {
			gpsStatus = 'Poor GPS accuracy';
			return;
		}

		if (lastPosition && position.timestamp <= lastPosition.timestamp) {
			return;
		}

		let calcSpeedKmh = 0;
		let segmentKm = 0;

		if (speed !== null && speed >= 0) {
			// speed is in m/s, convert to km/h
			calcSpeedKmh = speed * 3.6;
		}

		if (lastPosition) {
			segmentKm = calculateDistance(
				lastPosition.coords.latitude,
				lastPosition.coords.longitude,
				latitude,
				longitude
			);
			if (speed === null) {
				const timeDiffHours = (position.timestamp - lastPosition.timestamp) / 1000 / 3600;
				if (timeDiffHours > 0) {
					calcSpeedKmh = segmentKm / timeDiffHours;
				}
			}
		}

		if (calcSpeedKmh > 220) {
			return; // Ignore this point
		}

		currentSpeed = calcSpeedKmh;
		if (currentSpeed > maxSpeed) maxSpeed = currentSpeed;

		if (lastPosition) {
			if (segmentKm * 1000 < 3) {
				return;
			}
			distance += segmentKm;
		}

		const routePoint = {
			lat: latitude,
			lng: longitude,
			timestamp: new Date(position.timestamp).toISOString(),
			speed_kmh: Number(calcSpeedKmh.toFixed(2)),
			accuracy_m: accuracy,
			sequence: routePoints.length + 1
		};

		routePoints.push(routePoint);
		unsyncedPoints.push(routePoint);
		flushPoints();

		lastPosition = position;
		gpsStatus = 'Active';
	}

	onDestroy(() => {
		if (watchId !== null) navigator.geolocation.clearWatch(watchId);
		clearInterval(timerInterval);
		releaseWakeLock();
	});
</script>

<div class="container live-screen">
	<div class="status-bar">
		<span class="gps-indicator" class:active={gpsStatus === 'Active'}>
			<span class="dot"></span> {gpsStatus}
		</span>
		{#if isTracking}
			<span class="timer digital-font">{formatTime(elapsedSeconds)}</span>
		{/if}
	</div>

	<div class="speed-display">
		<div class="speed-value digital-font">{currentSpeed.toFixed(0)}</div>
		<div class="speed-unit">km/h</div>
	</div>

	<div class="stats-grid">
		<div class="card stat-card">
			<div class="stat-label">DISTANCE</div>
			<div class="stat-value digital-font">{distance.toFixed(2)} <span class="unit">km</span></div>
		</div>
		<div class="card stat-card">
			<div class="stat-label">AVG SPEED</div>
			<div class="stat-value digital-font">
				{#if elapsedSeconds > 0}
					{(distance / (elapsedSeconds / 3600)).toFixed(1)}
				{:else}
					0.0
				{/if}
				<span class="unit">km/h</span>
			</div>
		</div>
		<div class="card stat-card">
			<div class="stat-label">MAX SPEED</div>
			<div class="stat-value digital-font">{maxSpeed.toFixed(1)} <span class="unit">km/h</span></div>
		</div>
	</div>

	<div class="controls">
		{#if !isTracking}
			<button class="btn btn-primary start-btn" on:click={startTracking}>START TRIP</button>
		{:else}
			<button class="btn btn-danger stop-btn" on:click={stopTracking}>STOP TRIP</button>
		{/if}
	</div>
</div>

<style>
	.live-screen {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding-top: 2rem;
	}

	.status-bar {
		width: 100%;
		display: flex;
		justify-content: space-between;
		margin-bottom: 2rem;
		color: var(--text-secondary);
	}

	.gps-indicator {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.dot {
		width: 10px;
		height: 10px;
		border-radius: 50%;
		background-color: var(--danger-color);
	}

	.gps-indicator.active .dot {
		background-color: var(--accent-color);
		box-shadow: 0 0 8px var(--accent-color);
	}

	.timer {
		font-size: 1.2rem;
		color: var(--text-primary);
	}

	.speed-display {
		text-align: center;
		margin-bottom: 3rem;
	}

	.speed-value {
		font-size: 8rem;
		line-height: 1;
		color: var(--accent-color);
		text-shadow: 0 0 20px rgba(57, 255, 20, 0.3);
	}

	.speed-unit {
		font-size: 1.5rem;
		color: var(--text-secondary);
		text-transform: uppercase;
		letter-spacing: 2px;
	}

	.stats-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 1rem;
		width: 100%;
		margin-bottom: 3rem;
	}

	.stat-card {
		text-align: center;
		padding: 1rem;
	}

	.stat-label {
		font-size: 0.8rem;
		color: var(--text-secondary);
		margin-bottom: 0.5rem;
	}

	.stat-value {
		font-size: 1.5rem;
	}

	.unit {
		font-size: 0.8rem;
		color: var(--text-secondary);
	}

	.controls {
		width: 100%;
		display: flex;
		justify-content: center;
	}

	.start-btn, .stop-btn {
		width: 200px;
		height: 200px;
		border-radius: 50%;
		font-size: 1.5rem;
		box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
	}

	@media (max-width: 600px) {
		.speed-value {
			font-size: 6rem;
		}
		.stats-grid {
			gap: 0.5rem;
		}
		.stat-value {
			font-size: 1.2rem;
		}
		.start-btn, .stop-btn {
			width: 150px;
			height: 150px;
			font-size: 1.2rem;
		}
	}
</style>
