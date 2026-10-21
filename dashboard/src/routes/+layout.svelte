<script lang="ts">
	import './layout.css';
	import { page } from '$app/state';
	import {
		LayoutDashboard,
		Table2,
		FileText,
		ShieldAlert,
		ArrowUpRight,
		Layers3
	} from '@lucide/svelte';
	import type { LayoutProps } from './$types';
	let { children }: LayoutProps = $props();
	const links = [
		{ url: '/', label: 'Dashboard', icon: LayoutDashboard },
		{ url: '/dados', label: 'Explorar dados', icon: Table2 },
		{ url: '/relatorios', label: 'Relatórios', icon: FileText },
		{ url: '/risco', label: 'Sellers em risco', icon: ShieldAlert }
	];
</script>

<svelte:head
	><title>Vylo Customer Success</title><meta
		name="description"
		content="Acompanhe a saúde da carteira e priorize o relacionamento com seus sellers."
	/></svelte:head
>
<div class="app-shell">
	<aside class="sidebar">
		<a class="brand" href="/" aria-label="Vylo, início"
			><img src="/images/logo_white.png" alt="Vylo" /></a
		>
		<nav>
			{#each links as link}<a class:active={page.url.pathname === link.url} href={link.url}
					><link.icon size={19} />{link.label}{#if page.url.pathname === link.url}<span
							class="nav-dot"
						></span>{/if}</a
				>{/each}
		</nav>
	</aside>
	<div class="main-shell">
		<main>{@render children()}</main>
	</div>
</div>
