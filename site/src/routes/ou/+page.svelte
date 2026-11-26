<script lang="ts">
  import Enquete from '$lib/Enquete.svelte';

  let { data } = $props();
</script>

<svelte:head>
  <title>{data.enquete.meta.titre} · Puissance de calcul</title>
  <meta name="description" content={data.enquete.meta.question} />
</svelte:head>

<Enquete enquete={data.enquete} chiffres={data.chiffres} />
