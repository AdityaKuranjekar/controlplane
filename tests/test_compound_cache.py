from gateway.cache.semantic_cache import cache_store, cache_lookup, generate_compound_key

def test_compound_cache_isolation():
    prompt = "What is the revenue?"
    
    # Store response for internal_rag with Context A
    cache_store(
        query=prompt,
        response="Revenue is $10M for Company A",
        tier_used="tier0",
        profile_name="internal_rag",
        context_chunks=["Company A revenue in 2023 was $10M"]
    )
    
    # Lookup for same prompt but with Context B should MISS
    lookup_b = cache_lookup(
        query=prompt,
        profile_name="internal_rag",
        context_chunks=["Company B revenue in 2023 was $25M"]
    )
    assert lookup_b is None, "Expected cache MISS when RAG context differs!"
    
    # Lookup for same prompt and Context A should HIT
    lookup_a = cache_lookup(
        query=prompt,
        profile_name="internal_rag",
        context_chunks=["Company A revenue in 2023 was $10M"]
    )
    assert lookup_a is not None, "Expected cache HIT when prompt and context match!"
    assert lookup_a["response"] == "Revenue is $10M for Company A"
