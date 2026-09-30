// Static demo: every film's top 5 was precomputed by src/export.py.
// Reasons mirror MovieRecommender.explain() in src/recommender.py.
const films = await fetch('films.json').then((r) => r.json());
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
const norm = (s) => String(s).toLowerCase().normalize('NFKD').replace(/[^a-z0-9 ]/g, '').replace(/\s+/g, ' ').trim();
const list = (s) => String(s || '').split(' / ').filter(Boolean);
const index = films.map((f, i) => ({ i, key: norm(f.t) }));

function reasons(a, b) {
  const out = [];
  if (a.d && a.d === b.d) out.push(`Also directed by ${a.d}`);
  const cast = list(a.c).find((n) => list(b.c).includes(n));
  if (cast) out.push(`Also stars ${cast}`);
  const genres = list(a.g).filter((g) => list(b.g).includes(g)).slice(0, 3);
  if (genres.length) out.push(genres.join(' / '));
  const themes = list(a.k).filter((k) => list(b.k).includes(k)).slice(0, 3);
  if (themes.length) out.push('Themes: ' + themes.join(', '));
  return out;
}

// Exact title first, then titles that start with the query, then any match -
// each group ordered by how many votes the film has, so the well-known one wins.
function search(q, limit = 8) {
  const n = norm(q);
  if (!n) return [];
  const rank = (x) => (x.key === n ? 0 : x.key.startsWith(n) ? 1 : 2);
  return index
    .filter((x) => x.key.includes(n))
    .sort((a, b) => rank(a) - rank(b) || films[b.i].v - films[a.i].v)
    .slice(0, limit)
    .map((x) => x.i);
}

function show(i) {
  const f = films[i];
  $('q').value = f.t;
  closeList();
  $('result').innerHTML = `
    <div class="picked">
      <p class="k">Because you liked</p>
      <h2>${esc(f.t)} ${f.y ? `<span>(${f.y})</span>` : ''}</h2>
      <p class="meta">${esc(f.g)}${f.d ? ` · ${esc(f.d)}` : ''}</p>
    </div>
    <ol class="recs">
      ${f.r
        .map((j, rank) => {
          const r = films[j];
          return `<li class="card rec">
            <span class="rank">${rank + 1}</span>
            <div>
              <button type="button" class="title" data-i="${j}">${esc(r.t)} ${r.y ? `<span>(${r.y})</span>` : ''}</button>
              <p class="meta">${esc(r.g)}</p>
              <p class="why">${reasons(f, r).map((x) => `<span>${esc(x)}</span>`).join('')}</p>
            </div>
          </li>`;
        })
        .join('')}
    </ol>
    <p class="hint">Click any title to keep exploring.</p>`;
  history.replaceState(null, '', `?film=${encodeURIComponent(f.t)}`);
}

let active = -1;
function openList(ids) {
  const ul = $('list');
  active = -1;
  if (!ids.length) {
    ul.innerHTML = `<li class="none">No film by that name. Check the spelling, or try another.</li>`;
  } else {
    ul.innerHTML = ids
      .map((i) => `<li role="option" id="opt-${i}" data-i="${i}">${esc(films[i].t)} <span>${films[i].y ?? ''}</span></li>`)
      .join('');
  }
  ul.hidden = false;
  $('q').setAttribute('aria-expanded', 'true');
}
function closeList() {
  $('list').hidden = true;
  $('q').setAttribute('aria-expanded', 'false');
}

$('q').addEventListener('input', (e) => (e.target.value.trim() ? openList(search(e.target.value)) : closeList()));
$('q').addEventListener('keydown', (e) => {
  const opts = [...$('list').querySelectorAll('[data-i]')];
  if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
    e.preventDefault();
    if (!opts.length) return;
    active = (active + (e.key === 'ArrowDown' ? 1 : -1) + opts.length) % opts.length;
    opts.forEach((o, k) => o.classList.toggle('on', k === active));
    $('q').setAttribute('aria-activedescendant', opts[active].id);
  } else if (e.key === 'Enter') {
    e.preventDefault();
    const pick = opts[active] ?? opts[0];
    if (pick) show(Number(pick.dataset.i));
  } else if (e.key === 'Escape') closeList();
});
$('list').addEventListener('mousedown', (e) => {
  const li = e.target.closest('[data-i]');
  if (li) show(Number(li.dataset.i));
});
document.addEventListener('click', (e) => {
  const t = e.target.closest('[data-i].title, [data-film]');
  if (!t) return;
  if (t.dataset.film) {
    const hit = search(t.dataset.film, 1)[0];
    if (hit != null) show(hit);
  } else show(Number(t.dataset.i));
  window.scrollTo({ top: 0, behavior: 'smooth' });
});

const start = new URLSearchParams(location.search).get('film');
if (start) {
  const hit = search(start, 1)[0];
  if (hit != null) show(hit);
}
