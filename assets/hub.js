"use strict";
/**
 * games-hub.js — Games Hub Card Grid & Arena Controller
 */
(() => {
  const engine = window.__VakyaArcadeEngine;
  const GAMES = (window.__VakyaGamesPart1 || []).concat(window.__VakyaGamesPart2 || []);

  // Every (re)start of a round resets the touched/done tracking.
  GAMES.forEach(g => {
    const original = g.start;
    g.start = function (board) {
      engine.beginRound();
      return original.call(this, board);
    };
  });

  /* =========================================================================
   * 5. Public Arcade Interface
   * ========================================================================= */
  window.VakyaArcade = {
    games: GAMES,

    init(sentences) {
      engine.init(sentences);
      this.renderHub();
      const nextBtn = document.getElementById("btn-arcade-next");
      if (nextBtn) {
        nextBtn.onclick = () => {
          const board = document.getElementById("arcade-arena-board");
          if (engine.activeGame && board) engine.activeGame.start(board);
        };
      }
      const arenaBoard = document.getElementById("arcade-arena-board");
      if (arenaBoard) {
        // capture phase: runs before the game's own handler sees the click
        arenaBoard.addEventListener("click", e => {
          if (e.target.closest("button, .memory-card, .syntax-hi-word")) engine.markTouched();
        }, true);
      }
    },

    renderHub() {
      const grid = document.getElementById("arcade-games-grid");
      if (!grid) return;
      grid.innerHTML = GAMES.map(g => `
        <article class="arcade-game-card" data-game-id="${g.id}">
          <div class="arcade-card-icon-wrap" aria-hidden="true">
            <svg class="arcade-game-icon"><use href="#i-${g.icon || 'arcade'}"/></svg>
          </div>
          <div class="arcade-card-body">
            <h3 class="arcade-game-title">${g.title}</h3>
            ${g.tagline ? `<p class="arcade-game-tagline">${g.tagline}</p>` : ''}
          </div>
          <div class="arcade-card-arrow" aria-hidden="true">
            <svg class="arcade-arrow-icon" viewBox="0 0 24 24"><path d="M9 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </div>
        </article>
      `).join("");

      grid.onclick = e => {
        const card = e.target.closest(".arcade-game-card");
        if (card) {
          const gameId = card.dataset.gameId;
          this.launchGame(gameId);
        }
      };
    },

    launchGame(gameId) {
      const g = GAMES.find(x => x.id === gameId);
      if (!g) return;
      engine.activeGame = g;
      engine.stopTimer();

      // Show Arena Section
      const hubSec = document.getElementById("section-arcade-hub");
      const arenaSec = document.getElementById("section-arcade-arena");
      if (hubSec) hubSec.hidden = true;
      if (arenaSec) arenaSec.hidden = false;

      const titleEl = document.getElementById("arcade-arena-title");
      if (titleEl) titleEl.textContent = g.title;

      const board = document.getElementById("arcade-arena-board");
      if (board) g.start(board);
    },

    exitArena() {
      engine.stopTimer();
      engine.activeGame = null;
      const hubSec = document.getElementById("section-arcade-hub");
      const arenaSec = document.getElementById("section-arcade-arena");
      if (arenaSec) arenaSec.hidden = true;
      if (hubSec) hubSec.hidden = false;
    }
  };
})();
