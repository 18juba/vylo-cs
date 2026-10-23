<script lang="ts">
	import './layout.css';
	import { page } from '$app/state';
 import { onMount } from 'svelte';
 import { Menu, X } from '@lucide/svelte';
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
 let drawer: HTMLDialogElement;
 let menuOpen = $state(false);
 let menuButton: HTMLButtonElement;
 function closeMenu(){drawer?.close();menuOpen=false;}
 function openMenu(){drawer.showModal();menuOpen=true;}
 onMount(()=>{
  const media=window.matchMedia('(min-width: 1051px)');
  const resize=()=>{if(media.matches&&drawer.open)closeMenu();};
  media.addEventListener('change',resize);
  return()=>media.removeEventListener('change',resize);
 });
 $effect(()=>{
  if(!menuOpen)return;
  const previous=document.body.style.overflow;
  document.body.style.overflow='hidden';
  return()=>{document.body.style.overflow=previous;};
 });
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
{#snippet navigation()}
 <a class="brand" href="/" aria-label="Vylo, início" onclick={closeMenu}><img src="/images/logo_white.png" alt="Vylo" /></a>
 <nav class="drawer-nav" aria-label="Navegação principal">
 {#each links as link}<a class:active={page.url.pathname===link.url} aria-current={page.url.pathname===link.url?'page':undefined} href={link.url} onclick={closeMenu}><link.icon size={19}/>{link.label}{#if page.url.pathname===link.url}<span class="nav-dot"></span>{/if}</a>{/each}
 </nav>
{/snippet}
<div class="app-shell">
 <aside class="sidebar desktop-sidebar">{@render navigation()}</aside>
 <dialog bind:this={drawer} id="navigation-drawer" class="navigation-drawer" aria-label="Menu de navegação" onclose={()=>{menuOpen=false;menuButton?.focus();}} onpointerdown={(event)=>{if(event.target===drawer)closeMenu();}}>
  <div class="drawer-content"><button class="drawer-close" aria-label="Fechar menu" onclick={closeMenu}><X size={22}/></button>{@render navigation()}</div>
 </dialog>
 <div class="main-shell"><header class="mobile-header"><button bind:this={menuButton} class="menu-toggle" aria-label="Abrir menu" aria-expanded={menuOpen} aria-controls="navigation-drawer" onclick={openMenu}><Menu size={23}/></button><span>Vylo <strong>Customer Success</strong></span></header><main>{@render children()}</main></div>
</div>
