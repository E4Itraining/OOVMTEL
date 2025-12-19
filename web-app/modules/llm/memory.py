"""
Advanced Conversational Memory Module.

Provides sophisticated memory management for the SYNAPSIX AI assistant,
including context summarization, entity tracking, and long-term memory.
"""

import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
import hashlib
import json

logger = logging.getLogger(__name__)


class MemoryType(str, Enum):
    """Types of memory entries."""
    CONVERSATION = "conversation"
    ENTITY = "entity"
    PREFERENCE = "preference"
    INSIGHT = "insight"
    ACTION = "action"


@dataclass
class MemoryEntry:
    """A single memory entry."""
    id: str
    type: MemoryType
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    importance: float = 0.5  # 0-1 scale
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    def is_expired(self) -> bool:
        """Check if this memory entry has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def access(self):
        """Record an access to this memory."""
        self.access_count += 1
        self.last_accessed = datetime.utcnow()


@dataclass
class ConversationTurn:
    """A single turn in a conversation."""
    role: str  # user, assistant
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    intent: Optional[str] = None
    entities: Dict[str, Any] = field(default_factory=dict)
    tokens: int = 0


@dataclass
class ConversationSummary:
    """Summary of a conversation segment."""
    summary: str
    key_topics: List[str] = field(default_factory=list)
    entities_mentioned: Dict[str, List[str]] = field(default_factory=dict)
    actions_taken: List[str] = field(default_factory=list)
    unresolved_questions: List[str] = field(default_factory=list)
    turn_count: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)


class SessionMemory:
    """
    Memory management for a single conversation session.

    Features:
    - Short-term buffer for recent exchanges
    - Automatic summarization of older exchanges
    - Entity tracking across turns
    - Context window management
    """

    def __init__(
        self,
        session_id: str,
        max_buffer_turns: int = 10,
        max_summaries: int = 5,
        max_tokens_estimate: int = 4000
    ):
        """
        Initialize session memory.

        Args:
            session_id: Unique session identifier
            max_buffer_turns: Maximum turns to keep in active buffer
            max_summaries: Maximum number of summaries to retain
            max_tokens_estimate: Target token budget for context
        """
        self.session_id = session_id
        self.max_buffer_turns = max_buffer_turns
        self.max_summaries = max_summaries
        self.max_tokens_estimate = max_tokens_estimate

        # Active conversation buffer
        self._buffer: List[ConversationTurn] = []

        # Summarized history
        self._summaries: List[ConversationSummary] = []

        # Entity tracking
        self._entities: Dict[str, List[str]] = {
            "equipment": [],
            "metrics": [],
            "time_ranges": [],
            "production_lines": []
        }

        # Session metadata
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.turn_count = 0
        self.language = "fr"

        # User preferences for this session
        self._preferences: Dict[str, Any] = {}

    def add_turn(
        self,
        role: str,
        content: str,
        intent: Optional[str] = None,
        entities: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a conversation turn to memory.

        Args:
            role: Role of the speaker (user/assistant)
            content: Message content
            intent: Detected intent (if available)
            entities: Extracted entities (if available)
        """
        turn = ConversationTurn(
            role=role,
            content=content,
            intent=intent,
            entities=entities or {},
            tokens=self._estimate_tokens(content)
        )

        self._buffer.append(turn)
        self.turn_count += 1
        self.last_activity = datetime.utcnow()

        # Track entities
        if entities:
            self._track_entities(entities)

        # Check if summarization is needed
        if len(self._buffer) > self.max_buffer_turns:
            self._summarize_buffer()

    def _track_entities(self, entities: Dict[str, Any]) -> None:
        """Track entities mentioned in conversation."""
        for entity_type, values in entities.items():
            if entity_type in self._entities:
                if isinstance(values, list):
                    for v in values:
                        if v not in self._entities[entity_type]:
                            self._entities[entity_type].append(v)
                elif values and values not in self._entities[entity_type]:
                    self._entities[entity_type].append(values)

    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimation (4 chars per token average)."""
        return len(text) // 4

    def _summarize_buffer(self) -> None:
        """Summarize older turns and move to summary storage."""
        if len(self._buffer) <= self.max_buffer_turns // 2:
            return

        # Take the oldest half of the buffer for summarization
        to_summarize = self._buffer[:len(self._buffer) // 2]
        self._buffer = self._buffer[len(self._buffer) // 2:]

        # Generate summary
        summary = self._generate_summary(to_summarize)
        self._summaries.append(summary)

        # Trim old summaries if needed
        if len(self._summaries) > self.max_summaries:
            # Merge oldest summaries
            self._merge_old_summaries()

        logger.debug(f"Summarized {len(to_summarize)} turns for session {self.session_id}")

    def _generate_summary(self, turns: List[ConversationTurn]) -> ConversationSummary:
        """Generate a summary from conversation turns."""
        # Extract key information
        topics = set()
        entities = {}
        actions = []
        questions = []

        for turn in turns:
            if turn.intent:
                topics.add(turn.intent)

            for entity_type, values in turn.entities.items():
                if entity_type not in entities:
                    entities[entity_type] = []
                if isinstance(values, list):
                    entities[entity_type].extend(values)
                elif values:
                    entities[entity_type].append(values)

            # Simple heuristic for actions and questions
            content_lower = turn.content.lower()
            if turn.role == "assistant" and any(w in content_lower for w in ["recommande", "suggest", "devez", "should"]):
                actions.append(turn.content[:100])
            if turn.role == "user" and "?" in turn.content:
                questions.append(turn.content[:100])

        # Create summary text
        summary_parts = []
        if topics:
            summary_parts.append(f"Sujets: {', '.join(topics)}")
        if entities.get("equipment"):
            summary_parts.append(f"Équipements: {', '.join(set(entities['equipment']))}")
        if entities.get("metrics"):
            summary_parts.append(f"Métriques: {', '.join(set(entities['metrics']))}")

        summary_text = " | ".join(summary_parts) if summary_parts else "Conversation générale"

        return ConversationSummary(
            summary=summary_text,
            key_topics=list(topics),
            entities_mentioned=entities,
            actions_taken=actions[:3],
            unresolved_questions=questions[-2:],
            turn_count=len(turns)
        )

    def _merge_old_summaries(self) -> None:
        """Merge oldest summaries to save space."""
        if len(self._summaries) <= 2:
            return

        # Merge first two summaries
        s1, s2 = self._summaries[0], self._summaries[1]

        merged = ConversationSummary(
            summary=f"{s1.summary} → {s2.summary}",
            key_topics=list(set(s1.key_topics + s2.key_topics)),
            entities_mentioned={
                k: list(set(s1.entities_mentioned.get(k, []) + s2.entities_mentioned.get(k, [])))
                for k in set(list(s1.entities_mentioned.keys()) + list(s2.entities_mentioned.keys()))
            },
            actions_taken=(s1.actions_taken + s2.actions_taken)[-3:],
            unresolved_questions=s2.unresolved_questions,
            turn_count=s1.turn_count + s2.turn_count
        )

        self._summaries = [merged] + self._summaries[2:]

    def get_context(self, max_turns: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Get conversation context for LLM.

        Args:
            max_turns: Maximum recent turns to include

        Returns:
            List of message dictionaries for LLM context
        """
        context = []

        # Add summary context if available
        if self._summaries:
            summary_text = "Résumé de la conversation précédente:\n"
            for s in self._summaries[-2:]:
                summary_text += f"- {s.summary}\n"
            context.append({
                "role": "system",
                "content": summary_text
            })

        # Add recent turns
        turns = self._buffer if max_turns is None else self._buffer[-max_turns:]
        for turn in turns:
            context.append({
                "role": turn.role,
                "content": turn.content
            })

        return context

    def get_entity_context(self) -> str:
        """Get a formatted string of tracked entities."""
        parts = []

        if self._entities["equipment"]:
            parts.append(f"Équipements discutés: {', '.join(self._entities['equipment'][-5:])}")
        if self._entities["metrics"]:
            parts.append(f"Métriques analysées: {', '.join(self._entities['metrics'][-5:])}")
        if self._entities["production_lines"]:
            parts.append(f"Lignes de production: {', '.join(self._entities['production_lines'][-3:])}")

        return "\n".join(parts) if parts else ""

    def set_preference(self, key: str, value: Any) -> None:
        """Set a session preference."""
        self._preferences[key] = value

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a session preference."""
        return self._preferences.get(key, default)

    def get_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        return {
            "session_id": self.session_id,
            "turn_count": self.turn_count,
            "buffer_size": len(self._buffer),
            "summary_count": len(self._summaries),
            "entities_tracked": {k: len(v) for k, v in self._entities.items()},
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "language": self.language
        }

    def clear(self) -> None:
        """Clear all session memory."""
        self._buffer.clear()
        self._summaries.clear()
        for key in self._entities:
            self._entities[key].clear()
        self._preferences.clear()


class LongTermMemory:
    """
    Long-term memory for cross-session knowledge.

    Features:
    - User preference storage
    - Common query patterns
    - Equipment insights
    - Action history
    """

    def __init__(self, max_entries: int = 1000, ttl_days: int = 30):
        """
        Initialize long-term memory.

        Args:
            max_entries: Maximum memory entries to store
            ttl_days: Default time-to-live for entries
        """
        self.max_entries = max_entries
        self.ttl_days = ttl_days
        self._memories: Dict[str, MemoryEntry] = {}
        self._index: Dict[str, List[str]] = {}  # Type -> memory IDs

    def store(
        self,
        content: str,
        memory_type: MemoryType,
        metadata: Optional[Dict[str, Any]] = None,
        importance: float = 0.5,
        ttl_days: Optional[int] = None
    ) -> str:
        """
        Store a new memory entry.

        Args:
            content: Memory content
            memory_type: Type of memory
            metadata: Additional metadata
            importance: Importance score (0-1)
            ttl_days: Custom TTL (uses default if None)

        Returns:
            Memory entry ID
        """
        # Generate ID
        memory_id = hashlib.sha256(
            f"{content}{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]

        # Calculate expiry
        days = ttl_days if ttl_days is not None else self.ttl_days
        expires = datetime.utcnow() + timedelta(days=days) if days > 0 else None

        entry = MemoryEntry(
            id=memory_id,
            type=memory_type,
            content=content,
            metadata=metadata or {},
            importance=importance,
            expires_at=expires
        )

        self._memories[memory_id] = entry

        # Update index
        type_key = memory_type.value
        if type_key not in self._index:
            self._index[type_key] = []
        self._index[type_key].append(memory_id)

        # Cleanup if needed
        if len(self._memories) > self.max_entries:
            self._cleanup()

        return memory_id

    def retrieve(
        self,
        memory_type: Optional[MemoryType] = None,
        limit: int = 10,
        min_importance: float = 0.0
    ) -> List[MemoryEntry]:
        """
        Retrieve memory entries.

        Args:
            memory_type: Filter by type (None for all)
            limit: Maximum entries to return
            min_importance: Minimum importance score

        Returns:
            List of memory entries
        """
        if memory_type:
            ids = self._index.get(memory_type.value, [])
            entries = [self._memories[id] for id in ids if id in self._memories]
        else:
            entries = list(self._memories.values())

        # Filter expired and low importance
        entries = [
            e for e in entries
            if not e.is_expired() and e.importance >= min_importance
        ]

        # Sort by importance and recency
        entries.sort(
            key=lambda e: (e.importance, e.timestamp),
            reverse=True
        )

        # Mark as accessed
        for entry in entries[:limit]:
            entry.access()

        return entries[:limit]

    def search(self, query: str, limit: int = 5) -> List[MemoryEntry]:
        """
        Search memories by content.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            Matching memory entries
        """
        query_lower = query.lower()
        matches = []

        for entry in self._memories.values():
            if entry.is_expired():
                continue

            if query_lower in entry.content.lower():
                matches.append(entry)

        # Sort by relevance (simple frequency-based)
        matches.sort(
            key=lambda e: e.content.lower().count(query_lower),
            reverse=True
        )

        return matches[:limit]

    def update_importance(self, memory_id: str, importance: float) -> bool:
        """Update the importance of a memory entry."""
        if memory_id in self._memories:
            self._memories[memory_id].importance = min(1.0, max(0.0, importance))
            return True
        return False

    def delete(self, memory_id: str) -> bool:
        """Delete a memory entry."""
        if memory_id in self._memories:
            entry = self._memories[memory_id]
            del self._memories[memory_id]

            # Update index
            type_key = entry.type.value
            if type_key in self._index and memory_id in self._index[type_key]:
                self._index[type_key].remove(memory_id)

            return True
        return False

    def _cleanup(self) -> None:
        """Remove expired and low-importance entries."""
        to_remove = []

        for memory_id, entry in self._memories.items():
            if entry.is_expired():
                to_remove.append(memory_id)

        # If still over limit, remove least important
        if len(self._memories) - len(to_remove) > self.max_entries:
            remaining = [
                (id, e) for id, e in self._memories.items()
                if id not in to_remove
            ]
            remaining.sort(key=lambda x: (x[1].importance, x[1].access_count))

            excess = len(remaining) - self.max_entries
            for id, _ in remaining[:excess]:
                to_remove.append(id)

        for memory_id in to_remove:
            self.delete(memory_id)

        logger.debug(f"Cleaned up {len(to_remove)} memory entries")

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return {
            "total_entries": len(self._memories),
            "entries_by_type": {k: len(v) for k, v in self._index.items()},
            "max_entries": self.max_entries,
            "ttl_days": self.ttl_days
        }


class MemoryManager:
    """
    Central memory management for the assistant.

    Coordinates session and long-term memory.
    """

    def __init__(
        self,
        session_ttl_minutes: int = 60,
        max_sessions: int = 100
    ):
        """
        Initialize the memory manager.

        Args:
            session_ttl_minutes: Session inactivity timeout
            max_sessions: Maximum concurrent sessions
        """
        self.session_ttl = timedelta(minutes=session_ttl_minutes)
        self.max_sessions = max_sessions

        self._sessions: Dict[str, SessionMemory] = {}
        self._long_term = LongTermMemory()

    def get_session(self, session_id: str) -> SessionMemory:
        """
        Get or create a session memory.

        Args:
            session_id: Session identifier

        Returns:
            Session memory instance
        """
        if session_id not in self._sessions:
            self._cleanup_sessions()
            self._sessions[session_id] = SessionMemory(session_id)

        session = self._sessions[session_id]
        session.last_activity = datetime.utcnow()
        return session

    def _cleanup_sessions(self) -> None:
        """Remove inactive sessions."""
        now = datetime.utcnow()
        to_remove = []

        for session_id, session in self._sessions.items():
            if now - session.last_activity > self.session_ttl:
                to_remove.append(session_id)

        # Also remove if over limit
        if len(self._sessions) - len(to_remove) >= self.max_sessions:
            active = [
                (id, s) for id, s in self._sessions.items()
                if id not in to_remove
            ]
            active.sort(key=lambda x: x[1].last_activity)
            excess = len(active) - self.max_sessions + 1
            for id, _ in active[:excess]:
                to_remove.append(id)

        for session_id in to_remove:
            del self._sessions[session_id]

        if to_remove:
            logger.debug(f"Cleaned up {len(to_remove)} inactive sessions")

    def store_insight(
        self,
        content: str,
        equipment: Optional[str] = None,
        importance: float = 0.5
    ) -> str:
        """Store an equipment insight for future reference."""
        metadata = {}
        if equipment:
            metadata["equipment"] = equipment

        return self._long_term.store(
            content=content,
            memory_type=MemoryType.INSIGHT,
            metadata=metadata,
            importance=importance
        )

    def store_user_preference(
        self,
        user_id: str,
        preference_key: str,
        preference_value: Any
    ) -> str:
        """Store a user preference."""
        return self._long_term.store(
            content=json.dumps({"key": preference_key, "value": preference_value}),
            memory_type=MemoryType.PREFERENCE,
            metadata={"user_id": user_id},
            importance=0.7,
            ttl_days=365
        )

    def get_relevant_memories(
        self,
        query: str,
        session_id: Optional[str] = None,
        limit: int = 5
    ) -> List[MemoryEntry]:
        """
        Get memories relevant to a query.

        Args:
            query: Current query
            session_id: Current session ID
            limit: Maximum memories to return

        Returns:
            Relevant memory entries
        """
        return self._long_term.search(query, limit)

    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about active sessions."""
        return {
            "active_sessions": len(self._sessions),
            "max_sessions": self.max_sessions,
            "long_term_stats": self._long_term.get_stats()
        }


# Global memory manager instance
_memory_manager: Optional[MemoryManager] = None


def get_memory_manager() -> MemoryManager:
    """Get or create the global memory manager."""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager
