process CONVERT_SOFTCLIP_HARDCLIP {
    tag "$meta.id"
    label 'process_high'
    conda "conda-forge::pysam=0.23.3"
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/pysam:0.23.3--py39hdd5828d_1' :
        'biocontainers/pysam:0.23.3--py39hdd5828d_1' }"

    input:
    tuple val(meta), path(bam)

    output:
    path fastq           , emit: fastq
    path "versions.yml"  , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''
    def prefix = task.ext.prefix ?: "${meta.id}"

    """
    convert-softclip-to-hardclip.py \\
        --bam $bam \\
        --out ${prefix}.fq \\
        $args
        
    #compress
    gzip ${prefix}.fq 

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | sed 's/Python //g')
    END_VERSIONS
    """
}
