import pandas as pd

def main():
    all_fasta_csv_file_path = '/home/ec2-user/all_fasta.csv'
    hits_output_file_path = '/home/ec2-user/hits_output.csv'
    profile_out_file_path = '/home/ec2-user/profile_out.csv'


    df = pd.read_csv(all_fasta_csv_file_path)
    df_cleaned = df.dropna()
    df_cleaned = df_cleaned.rename(columns={'query_id': 'fasta_id', 'best_hit': 'best_hit_id'})
    df_cleaned[['fasta_id', 'best_hit_id']].to_csv(hits_output_file_path, index=False)

    ave_std = df_cleaned['score_std'].mean()
    ave_gmean = df_cleaned['score_gmean'].mean()

    profile_df = pd.DataFrame({'ave_std': [ave_std], 'ave_gmean': [ave_gmean]})
    profile_df.to_csv(profile_out_file_path, index=False)

if __name__ == "__main__":
    main()