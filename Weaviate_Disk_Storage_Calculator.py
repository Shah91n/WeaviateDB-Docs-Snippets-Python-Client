#!/usr/bin/env python3
"""
Weaviate Storage Calculator

This script estimates storage requirements for Weaviate vector database
based on number of documents, vector dimensions, and data characteristics.
"""

import argparse
import math
from typing import Dict, Any, Optional


def calculate_storage(
    num_documents: int,
    vector_dimensions: int,
    avg_document_size_bytes: int,
    quantization: Optional[str] = None,
    searchable_properties_ratio: float = 0.33,
    include_compression_comparison: bool = False
) -> Dict[str, Any]:
    """
    Calculate estimated storage requirements for Weaviate.
    
    Args:
        num_documents: Number of documents to be stored
        vector_dimensions: Dimensionality of vector embeddings (e.g., 768, 1536)
        avg_document_size_bytes: Average size of each document in bytes
        quantization: Type of quantization ('none', 'sq', 'pq', 'bq')
        searchable_properties_ratio: Ratio of index size to object size for searchable properties
        include_compression_comparison: Whether to include comparison of different compression options
        
    Returns:
        Dictionary with storage estimates
    """
    # Calculate vector storage (4 bytes per dimension for float32)
    bytes_per_vector = vector_dimensions * 4
    
    if quantization:
        quantization = quantization.lower()
        if quantization == 'sq':  # Scalar Quantization (8-bit)
            bytes_per_vector = vector_dimensions * 1  # 1 byte per dimension
        elif quantization == 'pq':  # Product Quantization
            # Simplified estimate - actual PQ depends on implementation details
            bytes_per_vector = vector_dimensions * 1  # Approximately 1 byte per dimension
        elif quantization == 'bq':  # Binary Quantization (1-bit)
            bytes_per_vector = math.ceil(vector_dimensions / 8)  # 1 bit per dimension
    
    total_vector_storage_bytes = num_documents * bytes_per_vector
    
    # Calculate document storage
    total_document_storage_bytes = num_documents * avg_document_size_bytes
    
    # Calculate searchable properties storage
    searchable_properties_bytes = total_document_storage_bytes * searchable_properties_ratio
    
    # Total storage
    total_storage_bytes = total_document_storage_bytes + total_vector_storage_bytes + searchable_properties_bytes
    
    # Prepare results
    results = {
        "input_parameters": {
            "num_documents": num_documents,
            "vector_dimensions": vector_dimensions,
            "avg_document_size_bytes": avg_document_size_bytes,
            "quantization": quantization if quantization else "none",
            "searchable_properties_ratio": searchable_properties_ratio
        },
        "storage_estimates": {
            "raw_document_storage_bytes": total_document_storage_bytes,
            "vector_storage_bytes": total_vector_storage_bytes,
            "searchable_properties_bytes": searchable_properties_bytes,
            "total_storage_bytes": total_storage_bytes,
            "total_storage_mb": total_storage_bytes / (1024 * 1024),
            "total_storage_gb": total_storage_bytes / (1024 * 1024 * 1024),
        }
    }
    
    # Add compression comparison if requested
    if include_compression_comparison:
        comparison = {}
        for quant_type in ["none", "sq", "pq", "bq"]:
            comp_bytes_per_vector = vector_dimensions * 4  # Default for no compression
            compression_ratio = 1
            
            if quant_type == "sq":
                comp_bytes_per_vector = vector_dimensions * 1  # 1 byte per dimension
                compression_ratio = 4
            elif quant_type == "pq":
                comp_bytes_per_vector = vector_dimensions * 1  # Approximate
                compression_ratio = 4
            elif quant_type == "bq":
                comp_bytes_per_vector = math.ceil(vector_dimensions / 8)  # 1 bit per dimension
                compression_ratio = 32
            
            comp_vector_storage = num_documents * comp_bytes_per_vector
            comp_total_storage = total_document_storage_bytes + comp_vector_storage + searchable_properties_bytes
            
            comparison[quant_type] = {
                "vector_storage_bytes": comp_vector_storage,
                "total_storage_bytes": comp_total_storage,
                "total_storage_mb": comp_total_storage / (1024 * 1024),
                "total_storage_gb": comp_total_storage / (1024 * 1024 * 1024),
                "compression_ratio": compression_ratio,
                "vector_storage_savings_percent": (1 - 1/compression_ratio) * 100 if compression_ratio > 1 else 0
            }
        
        results["compression_comparison"] = comparison
    
    return results


def format_bytes(bytes_value: float) -> str:
    """Format bytes to human-readable format."""
    if bytes_value < 1024:
        return f"{bytes_value:.2f} B"
    elif bytes_value < 1024 * 1024:
        return f"{bytes_value / 1024:.2f} KB"
    elif bytes_value < 1024 * 1024 * 1024:
        return f"{bytes_value / (1024 * 1024):.2f} MB"
    else:
        return f"{bytes_value / (1024 * 1024 * 1024):.2f} GB"


def print_results(results: Dict[str, Any]) -> None:
    """Print the results in a human-readable format."""
    print("\n======= WEAVIATE STORAGE CALCULATOR =======")
    print("\nInput Parameters:")
    params = results["input_parameters"]
    print(f"  Number of documents: {params['num_documents']:,}")
    print(f"  Vector dimensions: {params['vector_dimensions']}")
    print(f"  Average document size: {format_bytes(params['avg_document_size_bytes'])}")
    print(f"  Quantization method: {params['quantization']}")
    print(f"  Searchable properties ratio: {params['searchable_properties_ratio']}")
    
    print("\nStorage Estimates:")
    estimates = results["storage_estimates"]
    print(f"  Raw document storage: {format_bytes(estimates['raw_document_storage_bytes'])}")
    print(f"  Vector storage: {format_bytes(estimates['vector_storage_bytes'])}")
    print(f"  Searchable properties: {format_bytes(estimates['searchable_properties_bytes'])}")
    print(f"  Total storage: {format_bytes(estimates['total_storage_bytes'])} ({estimates['total_storage_gb']:.2f} GB)")
    
    if "compression_comparison" in results:
        print("\nCompression Options Comparison:")
        print(f"{'Method':<6} {'Vector Storage':<15} {'Total Storage':<15} {'Compression':<12} {'Savings'}")
        print(f"{'------':<6} {'---------------':<15} {'---------------':<15} {'------------':<12} {'-------'}")
        
        for method, data in results["compression_comparison"].items():
            print(f"{method:<6} {format_bytes(data['vector_storage_bytes']):<15} " 
                  f"{format_bytes(data['total_storage_bytes']):<15} "
                  f"{data['compression_ratio']:>5}x         "
                  f"{data['vector_storage_savings_percent']:.1f}%")
    
    print("\nNote: These are rough estimates based on simplified calculations.")
    print("For more accurate sizing, test with a sample (~100K documents) and extrapolate linearly.")
    print("Actual storage may scale sublinearly with increased document counts.")


def extrapolate_from_sample(
    sample_documents: int,
    sample_storage_bytes: int,
    target_documents: int
) -> Dict[str, Any]:
    """
    Extrapolate storage requirements from a sample dataset.
    
    Args:
        sample_documents: Number of documents in the sample
        sample_storage_bytes: Storage used by the sample in bytes
        target_documents: Target number of documents
        
    Returns:
        Dictionary with extrapolation results
    """
    # Linear extrapolation
    linear_storage = (sample_storage_bytes / sample_documents) * target_documents
    
    # Sublinear extrapolation (using a simple sqrt-based model as an example)
    # This is just an illustrative model - actual sublinear scaling depends on many factors
    sublinear_factor = math.sqrt(target_documents) / math.sqrt(sample_documents)
    sublinear_storage = sample_storage_bytes * sublinear_factor
    
    return {
        "sample_info": {
            "documents": sample_documents,
            "storage_bytes": sample_storage_bytes,
            "storage_per_document": sample_storage_bytes / sample_documents
        },
        "target_documents": target_documents,
        "linear_extrapolation": {
            "storage_bytes": linear_storage,
            "storage_mb": linear_storage / (1024 * 1024),
            "storage_gb": linear_storage / (1024 * 1024 * 1024)
        },
        "sublinear_extrapolation": {
            "storage_bytes": sublinear_storage,
            "storage_mb": sublinear_storage / (1024 * 1024),
            "storage_gb": sublinear_storage / (1024 * 1024 * 1024),
            "note": "This is an illustrative model only. Actual sublinear scaling depends on many factors."
        }
    }


def print_extrapolation_results(results: Dict[str, Any]) -> None:
    """Print extrapolation results in a human-readable format."""
    print("\n======= WEAVIATE STORAGE EXTRAPOLATION =======")
    print(f"\nSample information:")
    sample = results["sample_info"]
    print(f"  Sample size: {sample['documents']:,} documents")
    print(f"  Sample storage: {format_bytes(sample['storage_bytes'])}")
    print(f"  Storage per document: {format_bytes(sample['storage_per_document'])}")
    
    print(f"\nExtrapolation to {results['target_documents']:,} documents:")
    print(f"  Linear extrapolation: {format_bytes(results['linear_extrapolation']['storage_bytes'])} "
          f"({results['linear_extrapolation']['storage_gb']:.2f} GB)")
    print(f"  Sublinear example: {format_bytes(results['sublinear_extrapolation']['storage_bytes'])} "
          f"({results['sublinear_extrapolation']['storage_gb']:.2f} GB)")
    
    print("\nNote: Linear extrapolation provides a conservative estimate with buffer for planning.")
    print("      Actual storage often scales sublinearly as data size increases.")
    print("      The sublinear example is illustrative only and uses a simple model.")


def main():
    parser = argparse.ArgumentParser(description="Calculate storage requirements for Weaviate")
    
    # Create subparsers for different calculation modes
    subparsers = parser.add_subparsers(dest="mode", help="Calculation mode")
    
    # Parser for direct calculation
    calc_parser = subparsers.add_parser("calculate", help="Calculate storage based on parameters")
    calc_parser.add_argument("--documents", type=int, required=True, help="Number of documents")
    calc_parser.add_argument("--dimensions", type=int, required=True, help="Vector dimensions (e.g., 768, 1536)")
    calc_parser.add_argument("--doc-size", type=int, required=True, help="Average document size in bytes")
    calc_parser.add_argument("--quantization", choices=["none", "sq", "pq", "bq"], default="none", 
                            help="Quantization method (none, sq, pq, bq)")
    calc_parser.add_argument("--searchable-ratio", type=float, default=0.33, 
                            help="Ratio of index size to object size for searchable properties")
    calc_parser.add_argument("--compare-compression", action="store_true", 
                            help="Compare different compression options")
    
    # Parser for extrapolation from sample
    extrap_parser = subparsers.add_parser("extrapolate", help="Extrapolate from sample data")
    extrap_parser.add_argument("--sample-documents", type=int, required=True, 
                              help="Number of documents in sample")
    extrap_parser.add_argument("--sample-storage", type=float, required=True, 
                              help="Storage used by sample in MB")
    extrap_parser.add_argument("--target-documents", type=int, required=True, 
                              help="Target number of documents")
    
    args = parser.parse_args()
    
    if args.mode == "calculate":
        results = calculate_storage(
            num_documents=args.documents,
            vector_dimensions=args.dimensions,
            avg_document_size_bytes=args.doc_size,
            quantization=args.quantization,
            searchable_properties_ratio=args.searchable_ratio,
            include_compression_comparison=args.compare_compression
        )
        print_results(results)
        
    elif args.mode == "extrapolate":
        sample_storage_bytes = args.sample_storage * 1024 * 1024  # Convert MB to bytes
        results = extrapolate_from_sample(
            sample_documents=args.sample_documents,
            sample_storage_bytes=sample_storage_bytes,
            target_documents=args.target_documents
        )
        print_extrapolation_results(results)
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()