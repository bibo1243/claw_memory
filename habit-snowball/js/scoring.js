/**
 * Habit Snowball — Scoring Engine
 * 積分規則引擎：依據累計次數遞增加分，扣分規則，連續天數獎勵
 */

const ScoringEngine = (() => {
  /**
   * 根據累計進化/完成次數計算加分
   * 1-4次: +1, 5-9次: +3, 10-19次: +5, 20+次: +10
   */
  function getResistPoints(totalResisted) {
    if (totalResisted >= 20) return 10;
    if (totalResisted >= 10) return 5;
    if (totalResisted >= 5) return 3;
    return 1;
  }

  /**
   * 計算連續天數獎勵
   * 連續超過20天: 每天額外+15分
   */
  function getStreakBonus(currentStreak) {
    if (currentStreak > 20) return 15;
    return 0;
  }

  /**
   * 處理一次行動並回傳分數變化
   * @param {string} action - "resisted" | "urge" | "relapsed" | "completed"
   * @param {object} stats - 當前統計資料
   * @returns {object} { points, breakdown, newStats }
   */
  function processAction(action, stats) {
    const breakdown = [];
    let points = 0;
    const newStats = { ...stats };

    switch (action) {
      case 'resisted': // 進化了壞習慣
      case 'completed': { // 完成好習慣
        newStats.totalResisted = (newStats.totalResisted || 0) + 1;
        const resistPts = getResistPoints(newStats.totalResisted);
        points += resistPts;
        breakdown.push({
          label: action === 'resisted' ? '進化了' : '完成了',
          points: resistPts,
          detail: `第 ${newStats.totalResisted} 次（每次 +${resistPts}）`
        });

        // Check streak bonus
        const streakBonus = getStreakBonus(newStats.currentStreak);
        if (streakBonus > 0) {
          points += streakBonus;
          breakdown.push({
            label: '連續天數獎勵',
            points: streakBonus,
            detail: `連續 ${newStats.currentStreak} 天（每天 +${streakBonus}）`
          });
        }
        break;
      }

      case 'urge': // 有念頭（但沒做）
        points = -5;
        breakdown.push({
          label: '念起了',
          points: -5,
          detail: '超過10秒未覺察，念頭升起'
        });
        break;

      case 'relapsed': // 破戒了
        points = -20;
        breakdown.push({
          label: '破戒了',
          points: -20,
          detail: '實際做了壞習慣'
        });
        // Reset streak
        newStats.currentStreak = 0;
        break;
    }

    // Update total points (floor at 0)
    newStats.totalPoints = Math.max(0, (newStats.totalPoints || 0) + points);

    // Update longest streak
    if (newStats.currentStreak > (newStats.longestStreak || 0)) {
      newStats.longestStreak = newStats.currentStreak;
    }

    return { points, breakdown, newStats };
  }

  /**
   * 根據積分取得當前階段
   */
  function getStage(totalPoints) {
    if (totalPoints >= 1200) return { id: 'galaxy',  name: '星系',   emoji: '🌌', minPoints: 1200, nextPoints: null,  color1: '#8b5cf6', color2: '#06b6d4' };
    if (totalPoints >= 800)  return { id: 'star',    name: '恆星',   emoji: '⭐', minPoints: 800,  nextPoints: 1200, color1: '#fbbf24', color2: '#f472b6' };
    if (totalPoints >= 500)  return { id: 'planet',  name: '小星球', emoji: '🌍', minPoints: 500,  nextPoints: 800,  color1: '#34d399', color2: '#3b82f6' };
    if (totalPoints >= 300)  return { id: 'energy',  name: '能量球', emoji: '🌊', minPoints: 300,  nextPoints: 500,  color1: '#f59e0b', color2: '#ef4444' };
    if (totalPoints >= 150)  return { id: 'crystal', name: '水晶球', emoji: '🔮', minPoints: 150,  nextPoints: 300,  color1: '#c084fc', color2: '#f0abfc' };
    if (totalPoints >= 50)   return { id: 'ball',    name: '雪球',   emoji: '⚪', minPoints: 50,   nextPoints: 150,  color1: '#93c5fd', color2: '#e0f2fe' };
    return                          { id: 'flake',   name: '雪花',   emoji: '❄️', minPoints: 0,    nextPoints: 50,   color1: '#a8d8ea', color2: '#e0f0ff' };
  }

  /**
   * 計算到下一階段的進度百分比
   */
  function getStageProgress(totalPoints) {
    const stage = getStage(totalPoints);
    if (stage.nextPoints === null) return 100; // Max stage
    const progress = (totalPoints - stage.minPoints) / (stage.nextPoints - stage.minPoints);
    return Math.min(100, Math.max(0, progress * 100));
  }

  /**
   * 更新連續天數（每天檢查一次）
   * @param {string} lastActiveDate - ISO date string of last active day
   * @returns {object} { currentStreak, updated }
   */
  function updateStreak(lastActiveDate, currentStreak) {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

    if (!lastActiveDate) {
      return { currentStreak: 1, lastActiveDate: today.toISOString(), updated: true };
    }

    const lastDate = new Date(lastActiveDate);
    const lastDay = new Date(lastDate.getFullYear(), lastDate.getMonth(), lastDate.getDate());
    const diffDays = Math.floor((today - lastDay) / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
      // Same day, no change
      return { currentStreak, lastActiveDate: lastDay.toISOString(), updated: false };
    } else if (diffDays === 1) {
      // Consecutive day
      return { currentStreak: currentStreak + 1, lastActiveDate: today.toISOString(), updated: true };
    } else {
      // Streak broken
      return { currentStreak: 1, lastActiveDate: today.toISOString(), updated: true };
    }
  }

  return {
    processAction,
    getStage,
    getStageProgress,
    getResistPoints,
    getStreakBonus,
    updateStreak
  };
})();
