import asyncio
from app.services.rag_knowledge_base import RAGKnowledgeBase

async def verify_kb():
    kb = RAGKnowledgeBase()
    await kb.initialize()
    stats = await kb.get_stats()
    print(f"Total Entries: {stats['total_entries']}")
    print(f"Index Initialized: {stats['index_initialized']}")
    
    # Verify heuristics present
    heuristics = set()
    for entry in kb.knowledge_entries:
        heuristics.add(entry.get('heuristic_id'))
    
    print(f"Heuristics Covered: {sorted(list(heuristics))}")
    
    expected = {'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H10'}
    missing = expected - heuristics
    if not missing:
        print("SUCCESS: All heuristics covered!")
    else:
        print(f"FAILURE: Missing heuristics: {missing}")

if __name__ == "__main__":
    asyncio.run(verify_kb())
