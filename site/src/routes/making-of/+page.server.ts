import { sectionsMakingOf } from '$lib/server/makingof';

export const prerender = true;

export function load() {
  return { sections: sectionsMakingOf() };
}
