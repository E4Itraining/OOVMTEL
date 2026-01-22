# Guide: Comprendre les Métriques LLM

Ce guide vous aide à interpréter les métriques d'observabilité LLM de SYNAPSIX pour optimiser vos performances et maîtriser vos coûts.

---

## Table des matières

1. [Métriques de Latence](#métriques-de-latence)
2. [Métriques de Tokens](#métriques-de-tokens)
3. [Métriques de Coûts](#métriques-de-coûts)
4. [Métriques d'Erreurs](#métriques-derreurs)
5. [Alertes et Seuils](#alertes-et-seuils)
6. [Actions Recommandées](#actions-recommandées)
7. [Glossaire](#glossaire)

---

## Métriques de Latence

### Qu'est-ce que la latence?

La **latence** mesure le temps entre l'envoi d'une requête au modèle LLM et la réception de la réponse complète.

### Percentiles expliqués

| Métrique | Signification | Exemple |
|----------|---------------|---------|
| **P50** | 50% des requêtes sont plus rapides | P50 = 1000ms → La moitié des requêtes prend moins d'1 seconde |
| **P95** | 95% des requêtes sont plus rapides | P95 = 3000ms → Seules 5% des requêtes dépassent 3 secondes |
| **P99** | 99% des requêtes sont plus rapides | P99 = 5000ms → Seul 1% des requêtes dépasse 5 secondes |
| **Moyenne** | Latence moyenne | Moyenne = 1500ms |

### Seuils recommandés

| Niveau | Latence P95 | Action |
|--------|-------------|--------|
| 🟢 Excellent | < 2 secondes | Aucune action |
| 🟡 Acceptable | 2-5 secondes | Surveiller |
| 🟠 Attention | 5-15 secondes | Optimiser les prompts |
| 🔴 Critique | > 15 secondes | Action immédiate requise |

### Facteurs impactant la latence

1. **Taille du prompt** - Plus le prompt est long, plus la latence augmente
2. **Max tokens demandés** - Plus de tokens = plus de temps de génération
3. **Modèle utilisé** - Les modèles plus grands sont plus lents
4. **Charge du provider** - Pics de trafic chez le fournisseur

---

## Métriques de Tokens

### Qu'est-ce qu'un token?

Un **token** est une unité de texte (environ 4 caractères ou ¾ d'un mot en anglais). Les modèles LLM facturent par token.

### Types de tokens

| Type | Description | Coût relatif |
|------|-------------|--------------|
| **Prompt tokens** | Tokens envoyés (votre question + contexte) | Moins cher |
| **Completion tokens** | Tokens générés (la réponse) | Plus cher |
| **Total tokens** | Prompt + Completion | - |

### Exemple concret

```
Prompt: "Explique-moi ce qu'est l'OEE en 2 phrases."
→ ~12 tokens de prompt

Réponse: "L'OEE (Overall Equipment Effectiveness) est un indicateur..."
→ ~50 tokens de completion

Total: ~62 tokens
```

### Optimisation des tokens

| Technique | Économie potentielle |
|-----------|---------------------|
| Prompts concis | -30% à -50% |
| Limiter max_tokens | Variable |
| Utiliser le prompt caching (Claude) | -50% à -90% sur prompts répétés |
| Choisir le bon modèle | -50% à -80% |

---

## Métriques de Coûts

### Comment sont calculés les coûts?

Les coûts sont estimés selon les tarifs des providers:

| Provider | Prompt ($/1M tokens) | Completion ($/1M tokens) |
|----------|---------------------|--------------------------|
| **Mistral** | $2.00 | $6.00 |
| **Claude** | $3.00 | $15.00 |
| **OpenAI GPT-4** | $5.00 | $15.00 |
| **Ollama** | $0.00 | $0.00 (local) |

### Exemple de calcul

```
1000 requêtes avec Mistral:
- Moyenne 500 tokens prompt / requête
- Moyenne 200 tokens completion / requête

Coût prompt: 500,000 tokens × $2/1M = $1.00
Coût completion: 200,000 tokens × $6/1M = $1.20
Total: $2.20 pour 1000 requêtes
```

### Alertes de budget

| Seuil | Valeur par défaut | Configurable |
|-------|-------------------|--------------|
| Budget horaire | $20.00 | `LLM_ALERT_HOURLY_COST_LIMIT_USD` |
| Budget journalier | $100.00 | `LLM_ALERT_DAILY_COST_LIMIT_USD` |

---

## Métriques d'Erreurs

### Taux d'erreur

Le **taux d'erreur** = (Requêtes échouées / Total requêtes) × 100

| Taux | Niveau | Action |
|------|--------|--------|
| < 1% | 🟢 Normal | Aucune |
| 1-5% | 🟡 Attention | Surveiller |
| 5-10% | 🟠 Problème | Investiguer |
| > 10% | 🔴 Critique | Action immédiate |

### Catégories d'erreurs

| Catégorie | Cause | Solution |
|-----------|-------|----------|
| **Rate Limit** | Trop de requêtes | Ajouter du délai, upgrade plan |
| **Timeout** | Requête trop longue | Réduire max_tokens |
| **Authentication** | Clé API invalide | Vérifier la configuration |
| **Quota Exceeded** | Budget épuisé | Augmenter quota |
| **Content Policy** | Contenu filtré | Modifier le prompt |
| **Model Unavailable** | Modèle indisponible | Utiliser un fallback |

---

## Alertes et Seuils

### Configuration des alertes

| Alerte | Seuil Warning | Seuil Critical |
|--------|---------------|----------------|
| Latence P95 | 5 secondes | 15 secondes |
| Taux d'erreur | 5% | 10% |
| Tokens/heure | 80% du quota | 100% du quota |
| Coût/heure | 80% du budget | 100% du budget |

### Personnaliser les seuils

```bash
# Variables d'environnement
LLM_ALERT_LATENCY_WARNING_MS=5000
LLM_ALERT_LATENCY_CRITICAL_MS=15000
LLM_ALERT_ERROR_RATE_WARNING_PCT=5.0
LLM_ALERT_ERROR_RATE_CRITICAL_PCT=10.0
LLM_ALERT_HOURLY_TOKEN_LIMIT=100000
LLM_ALERT_HOURLY_COST_LIMIT_USD=20.0
```

---

## Actions Recommandées

### Si la latence est élevée

1. ✅ Vérifier la taille de vos prompts
2. ✅ Réduire `max_tokens` si possible
3. ✅ Considérer un modèle plus rapide (ex: Mistral Small)
4. ✅ Vérifier le status du provider

### Si le taux d'erreur augmente

1. ✅ Identifier la catégorie d'erreur dominante
2. ✅ Vérifier les quotas API
3. ✅ Implémenter des retries avec backoff
4. ✅ Configurer un provider de fallback

### Si les coûts explosent

1. ✅ Analyser les requêtes les plus coûteuses
2. ✅ Optimiser les prompts répétitifs
3. ✅ Activer le prompt caching (Claude)
4. ✅ Envisager un modèle moins cher ou local (Ollama)

---

## Glossaire

| Terme | Définition |
|-------|------------|
| **LLM** | Large Language Model - Modèle de langage comme GPT, Claude, Mistral |
| **Token** | Unité de texte (~4 caractères) utilisée pour la facturation |
| **Latence** | Temps de réponse du modèle |
| **P95/P99** | Percentiles statistiques |
| **Prompt** | Texte envoyé au modèle (question + contexte) |
| **Completion** | Réponse générée par le modèle |
| **Rate Limit** | Limite de requêtes par minute/heure |
| **Prompt Caching** | Réutilisation de prompts similaires pour réduire les coûts |
| **TTFT** | Time To First Token - Temps avant le premier token en streaming |
| **Provider** | Fournisseur de service LLM (Mistral, OpenAI, Anthropic...) |

---

## Ressources Complémentaires

- [Dashboard Grafana LLM Observability](/grafana/d/llm-observability)
- [Configuration des alertes](/docs/configuration/llm-observability#alerting)
- [API Reference](/docs/api/llm-observability)
- [Troubleshooting](/docs/troubleshooting/llm-observability)

---

*Guide mis à jour le 2026-01-22 - SYNAPSIX v1.2.0*
