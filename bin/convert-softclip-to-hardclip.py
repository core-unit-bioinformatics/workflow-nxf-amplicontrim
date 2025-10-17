#!/usr/bin/env python3
"""
Convert a BAM file to FASTQ, removing soft-clipped bases.
Designed for single-end reads.
"""

import pysam
import argparse
import os
import sys

def parse_args():
    """Parse and check command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert BAM to FASTQ, removing soft-clipped bases."
    )
    parser.add_argument(
        "-b", "--bam", required=True, help="Input BAM file (must be sorted/indexed)"
    )
    parser.add_argument(
        "-o", "--out", default=None, help="Output FASTQ file (default: BAM filename with .fastq)"
    )
    args = parser.parse_args()

    # Check input BAM filename
    if not args.bam.endswith(".bam"):
        print("Error: Input file does not have '.bam' extension.", file=sys.stderr)
        sys.exit(1)

    # Set default output filename if not provided
    if args.out is None:
        args.out = os.path.splitext(args.bam)[0] + ".fastq"

    return args


def trim_soft_clips(read):
    """
    Remove soft-clipped bases from a pysam.AlignedSegment.

    Args:
        read (pysam.AlignedSegment): A single read from BAM file.

    Returns:
        tuple: (trimmed_sequence, trimmed_quality_string)
    """
    seq = read.query_sequence
    qual = read.query_qualities

    new_seq = ""
    new_qual = []

    query_pos = 0
    for (cigar_type, length) in read.cigartuples:
        if cigar_type == 4:  # 4 = soft clip
            query_pos += length  # skip soft-clipped bases
        else:
            new_seq += seq[query_pos:query_pos+length]
            new_qual.extend(qual[query_pos:query_pos+length])
            query_pos += length

    # Convert quality scores to ASCII (Phred+33)
    new_qual_str = "".join([chr(q + 33) for q in new_qual])

    return new_seq, new_qual_str


def bam_to_fastq_no_softclip(bam_file, fastq_file):
    """
    Convert a BAM file to FASTQ, removing soft-clipped bases.

    Args:
        bam_file (str): Input BAM file path.
        fastq_file (str): Output FASTQ file path.
    """
    with pysam.AlignmentFile(bam_file, "rb") as bam, open(fastq_file, "w") as fq_out:
        for read in bam:
            if read.is_unmapped:
                continue

            trimmed_seq, trimmed_qual = trim_soft_clips(read)

            fq_out.write(f"@{read.query_name}\n{trimmed_seq}\n+\n{trimmed_qual}\n")


def main():
    """Main function."""
    args = parse_args()
    bam_to_fastq_no_softclip(args.bam, args.out)
    print(f"Finished! Output FASTQ written to: {args.out}")


if __name__ == "__main__":
    main()
