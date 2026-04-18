'use client';

import React, { useEffect, useState } from 'react';
import { useStore } from '@/lib/store';
import { TrendingUp, TrendingDown, Brain, AlertCircle, CheckCircle2 } from 'lucide-react';

interface DecisionState {
  action: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  reasoning: string[];
  components: {
    ml_component: number;
    technical_component: number;
    sentiment_component: number;
  };
  technical_signals?: {
    rsi?: number;
    rsi_oversold?: boolean;
    rsi_overbought?: boolean;
    macd_bullish?: boolean;
    macd_crossover?: boolean;
    ema_bullish_cross?: boolean;
    volatility?: number;
    technical_score?: number;
  };
  timestamp: string;
}

interface VolatilityRegime {
  regime: 'LOW' | 'NORMAL' | 'HIGH' | 'EXTREME';
  current_atr: number;
  historical_volatility: number;
}

export function AgentBrain() {
  useStore((store) => store.decision);
  const [decision, setDecision] = useState<DecisionState | null>(null);
  const [volatilityRegime, setVolatilityRegime] = useState<VolatilityRegime | null>(null);
  const [isLive, setIsLive] = useState(false);

  useEffect(() => {
    // Connect to WebSocket for real-time updates
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/decisions`);

    ws.onopen = () => {
      setIsLive(true);
      console.log('🧠 Live Agent Brain connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'decision') {
          setDecision(data.payload);
        } else if (data.type === 'volatility') {
          setVolatilityRegime(data.payload);
        }
      } catch (e) {
        console.error('WebSocket parse error:', e);
      }
    };

    ws.onerror = () => setIsLive(false);
    ws.onclose = () => setIsLive(false);

    return () => ws.close();
  }, []);

  if (!decision) {
    return (
      <div className="bg-slate-900 border border-slate-700 rounded-lg p-6">
        <div className="flex items-center gap-3 mb-4">
          <Brain className="w-6 h-6 text-cyan-400" />
          <h2 className="text-lg font-bold text-white">Live Agent Brain</h2>
          <div className="ml-auto flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${isLive ? 'bg-green-400' : 'bg-slate-500'}`} />
            <span className="text-xs text-slate-400">{isLive ? 'LIVE' : 'OFFLINE'}</span>
          </div>
        </div>
        <div className="text-slate-400 text-sm">Waiting for first decision...</div>
      </div>
    );
  }

  const actionColor = {
    BUY: 'text-green-400',
    SELL: 'text-red-400',
    HOLD: 'text-amber-400',
  };

  const actionBg = {
    BUY: 'bg-green-500/20 border-green-500/50',
    SELL: 'bg-red-500/20 border-red-500/50',
    HOLD: 'bg-amber-500/20 border-amber-500/50',
  };

  const confidencePercent = Math.round(decision.confidence * 100);
  const confidenceColor = confidencePercent >= 75 ? 'text-green-400' : confidencePercent >= 60 ? 'text-amber-400' : 'text-red-400';

  return (
    <div className="space-y-4">
      {/* Main Decision Card */}
      <div className={`border rounded-lg p-6 ${actionBg[decision.action]}`}>
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            {decision.action === 'BUY' ? (
              <TrendingUp className={`w-8 h-8 ${actionColor[decision.action]}`} />
            ) : decision.action === 'SELL' ? (
              <TrendingDown className={`w-8 h-8 ${actionColor[decision.action]}`} />
            ) : (
              <AlertCircle className={`w-8 h-8 ${actionColor[decision.action]}`} />
            )}
            <div>
              <h3 className={`text-2xl font-bold ${actionColor[decision.action]}`}>{decision.action}</h3>
              <p className="text-xs text-slate-400">Decision at {new Date(decision.timestamp).toLocaleTimeString()}</p>
            </div>
          </div>
          <div className="text-right">
            <div className={`text-3xl font-bold ${confidenceColor}`}>{confidencePercent}%</div>
            <p className="text-xs text-slate-400">Confidence</p>
          </div>
        </div>

        {/* Confidence Bar */}
        <div className="mb-4">
          <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
            <div
              className={`h-full transition-all duration-500 ${
                confidencePercent >= 75 ? 'bg-green-500' : confidencePercent >= 60 ? 'bg-amber-500' : 'bg-red-500'
              }`}
              style={{ width: `${confidencePercent}%` }}
            />
          </div>
        </div>
      </div>

      {/* Reasoning Section */}
      <div className="bg-slate-900 border border-slate-700 rounded-lg p-6">
        <h4 className="text-sm font-semibold text-cyan-400 mb-4 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4" />
          Why This Decision?
        </h4>
        <div className="space-y-3">
          {decision.reasoning.slice(0, 3).map((reason, idx) => (
            <div key={idx} className="flex items-start gap-3 bg-slate-800/50 rounded p-3 border-l-2 border-cyan-500">
              <span className="text-cyan-400 font-bold text-sm">{idx + 1}.</span>
              <span className="text-slate-200 text-sm">{reason}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Technical Signals */}
      {decision.technical_signals && (
        <div className="bg-slate-900 border border-slate-700 rounded-lg p-6">
          <h4 className="text-sm font-semibold text-purple-400 mb-4">Technical Signals</h4>
          <div className="grid grid-cols-2 gap-4">
            {/* RSI */}
            {decision.technical_signals.rsi !== undefined && (
              <div className="bg-slate-800/50 rounded p-3 border border-slate-700">
                <p className="text-xs text-slate-400 mb-1">RSI (14)</p>
                <p className="text-lg font-bold text-white">{decision.technical_signals.rsi.toFixed(1)}</p>
                <p className="text-xs text-slate-500 mt-1">
                  {decision.technical_signals.rsi_oversold ? '📉 Oversold' : decision.technical_signals.rsi_overbought ? '📈 Overbought' : '⚖️ Neutral'}
                </p>
              </div>
            )}

            {/* MACD */}
            {decision.technical_signals.macd_bullish !== undefined && (
              <div className="bg-slate-800/50 rounded p-3 border border-slate-700">
                <p className="text-xs text-slate-400 mb-1">MACD</p>
                <p className={`text-lg font-bold ${decision.technical_signals.macd_bullish ? 'text-green-400' : 'text-red-400'}`}>
                  {decision.technical_signals.macd_bullish ? '📈 Bullish' : '📉 Bearish'}
                </p>
                {decision.technical_signals.macd_crossover && <p className="text-xs text-yellow-400 mt-1">↔️ Crossover</p>}
              </div>
            )}

            {/* EMA */}
            {decision.technical_signals.ema_bullish_cross !== undefined && (
              <div className="bg-slate-800/50 rounded p-3 border border-slate-700">
                <p className="text-xs text-slate-400 mb-1">EMA Trend</p>
                <p className={`text-lg font-bold ${decision.technical_signals.ema_bullish_cross ? 'text-green-400' : 'text-red-400'}`}>
                  {decision.technical_signals.ema_bullish_cross ? '📈 Bullish' : '📉 Bearish'}
                </p>
              </div>
            )}

            {/* Volatility */}
            {decision.technical_signals.volatility !== undefined && (
              <div className="bg-slate-800/50 rounded p-3 border border-slate-700">
                <p className="text-xs text-slate-400 mb-1">Volatility</p>
                <p className="text-lg font-bold text-white">{(decision.technical_signals.volatility * 100).toFixed(1)}%</p>
                <p className="text-xs text-slate-500 mt-1">Realized</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Decision Components */}
      <div className="bg-slate-900 border border-slate-700 rounded-lg p-6">
        <h4 className="text-sm font-semibold text-blue-400 mb-4">Decision Breakdown</h4>
        <div className="space-y-3">
          {/* ML Component */}
          <div>
            <div className="flex justify-between items-center mb-1">
              <span className="text-xs text-slate-300">ML Prediction</span>
              <span className="text-xs font-bold text-blue-400">{(decision.components.ml_component * 100).toFixed(0)}%</span>
            </div>
            <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
              <div className="h-full bg-blue-500" style={{ width: `${decision.components.ml_component * 100}%` }} />
            </div>
          </div>

          {/* Technical Component */}
          <div>
            <div className="flex justify-between items-center mb-1">
              <span className="text-xs text-slate-300">Technical Analysis</span>
              <span className="text-xs font-bold text-purple-400">{(decision.components.technical_component * 100).toFixed(0)}%</span>
            </div>
            <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
              <div className="h-full bg-purple-500" style={{ width: `${decision.components.technical_component * 100}%` }} />
            </div>
          </div>

          {/* Sentiment Component */}
          <div>
            <div className="flex justify-between items-center mb-1">
              <span className="text-xs text-slate-300">Market Sentiment</span>
              <span className="text-xs font-bold text-amber-400">{(decision.components.sentiment_component * 100).toFixed(0)}%</span>
            </div>
            <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
              <div className="h-full bg-amber-500" style={{ width: `${decision.components.sentiment_component * 100}%` }} />
            </div>
          </div>
        </div>
      </div>

      {/* Volatility Regime */}
      {volatilityRegime && (
        <div className="bg-slate-900 border border-slate-700 rounded-lg p-6">
          <h4 className="text-sm font-semibold text-orange-400 mb-4">Market Conditions</h4>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-slate-400 mb-1">Volatility Regime</p>
              <p className={`text-lg font-bold ${volatilityRegime.regime === 'EXTREME' ? 'text-red-400' : volatilityRegime.regime === 'HIGH' ? 'text-orange-400' : 'text-green-400'}`}>
                {volatilityRegime.regime}
              </p>
            </div>
            <div>
              <p className="text-xs text-slate-400 mb-1">ATR</p>
              <p className="text-lg font-bold text-white">${volatilityRegime.current_atr.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-xs text-slate-400 mb-1">Realized Vol</p>
              <p className="text-lg font-bold text-white">{(volatilityRegime.historical_volatility * 100).toFixed(1)}%</p>
            </div>
          </div>
        </div>
      )}

      {/* Status Indicator */}
      <div className="flex items-center gap-2 text-xs text-slate-400 bg-slate-800 rounded p-3 border border-slate-700">
        <div className={`w-2 h-2 rounded-full ${isLive ? 'bg-green-400 animate-pulse' : 'bg-slate-500'}`} />
        {isLive ? '🧠 Agent Brain ACTIVE - Monitoring market in real-time' : '⏸️ Offline - Awaiting connection'}
      </div>
    </div>
  );
}
