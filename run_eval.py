import json
import numpy as np
from evaluation.evaluate import evaluate

from app.services.chat_service import answer_question

# 1. Simulate running your RAG system over the 30 test cases
def generate_rag_results(input_dataset_path, output_dataset_path):
    with open(input_dataset_path, 'r', encoding='utf-8') as f:
        test_cases = json.load(f)
    
    evaluated_samples = []
    
    for i, case in enumerate(test_cases):
        question = case["question"]
        
        question = case["question"]
        print(f"   [{i+1}/{len(test_cases)}] Processing: '{question[:40]}...'")
        
        # 2. CREATE A UNIQUE ISOLATED EVAL USER ID FOR MEMORY CLEANLINESS
        eval_user_id = f"eval_test_user_{i}"
        
        # 3. EXECUTE YOUR REAL PIPELINE
        pipeline_output = answer_question(user_id=eval_user_id, query=question)
        
        # 4. EXTRACT THE PREDICTION AND DATA RETRIEVED
        prediction_text = pipeline_output.get("answer", "")
        
        # Gather all structural string IDs from the sources dictionary payload 
        # (e.g., "genesis_1_1_10", "wsc_1")
        retrieved_ids = [source["id"] for source in pipeline_output.get("sources", [])]
        
        # Build the exact dictionary structure evaluate.py requires
        evaluated_samples.append({
            "question": question,
            "answer": case["answer"],          # Gold answer
            "relevant_docs": case["relevant_docs"],  # Gold doc IDs
            "prediction": prediction_text,     # RAG LLM's output
            "retrieved_docs": retrieved_ids # Chunk IDs your retriever fetched
        })
        
    with open(output_dataset_path, 'w', encoding='utf-8') as f:
        json.dump(evaluated_samples, f, indent=2)

#  Run the metrics evaluation and aggregate results
def main():
    input_json = "evaluation/eval_dataset.json"          
    pipeline_results_json = "results_to_score.json" # Temporary file for evaluation
    
    print(" Processing questions through RAG pipeline...")
    generate_rag_results(input_json, pipeline_results_json)
    
    print(" Calculating retrieval and text metrics...")
    retrieval_res, answer_res = evaluate(pipeline_results_json)
    
    # Aggregate Retrieval Averages
    avg_recall = np.mean([r["recall"] for r in retrieval_res])
    avg_precision = np.mean([r["precision"] for r in retrieval_res])
    avg_hit_rate = np.mean([r["hit_rate"] for r in retrieval_res])
    
    # Aggregate Generation Averages
    avg_r1 = np.mean([a["rouge1"] for a in answer_res])
    avg_r2 = np.mean([a["rouge2"] for a in answer_res])
    avg_rl = np.mean([a["rougeL"] for a in answer_res])
    
    # Print a clean evaluation report
    print("\n" + "="*40)
    print("          RAG EVALUATION REPORT         ")
    print("="*40)
    print(f"Total Test Cases Processed: {len(retrieval_res)}")
    print("-"*40)
    print(f"Retrieval Hit Rate:    {avg_hit_rate:.4f}")
    print(f"Retrieval Recall:      {avg_recall:.4f}")
    print(f"Retrieval Precision:   {avg_precision:.4f}")
    print("-"*40)
    print(f"ROUGE-1 F-Measure:     {avg_r1:.4f}")
    print(f"ROUGE-2 F-Measure:     {avg_r2:.4f}")
    print(f"ROUGE-L F-Measure:     {avg_rl:.4f}")
    print("="*40)

if __name__ == "__main__":
    main()