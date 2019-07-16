from zipper_utils import *


def zipper(zf_dir_path,struct_file,th_to_prove_file=None):

	struct_dict = json_to_list_or_dict(struct_file)


	threads=[]

	for chapter in struct_dict :
	    
		zipper_exec_time[chapter]=dict()

		if th_to_prove_file is None :
			for lemme in struct_dict[chapter] :
				threads.append(Zipperposition(zf_dir_path,chapter,lemme))
		else :
			th_to_prove= json_to_list_or_dict(th_to_prove_file)
			for lemme in struct_dict[chapter] :
				if lemme in th_to_prove :
					threads.append(Zipperposition(zf_dir_path,chapter,lemme))

	for i in range(len(threads)):
		with semZ :
			threads[i].start()

	for i in range(len(threads)):
	    threads[i].join()

	print("done")

	return get_zipper_stat(zipper_exec_time)


if __name__ == "__main__":
	if len(sys.argv) < 4 :
		print("Prend en parametre :\n zf_dir : dossier contenant les fichiers de preuves\n th_valid_file : le fichier dans lequel seront stockés les noms des théorèmes ainsi prouvés (json)\n config_struct : nom du fichier spécifiant la structure du contenu du dossier zf_dir\n th_to_prove_file : fichier contenant les noms des theoremes a traiter par le script (json) (default : tout les theoremes sont pris en compte)")
	else :
		if len(sys.argv) == 4 :
			(done,notdone,gaveup,ressourceout,timeout)=zipper(sys.argv[1],sys.argv[3],None)
			list_or_dict_to_json(done,sys.argv[2])
			print(zipper_stat(done,notdone,gaveup,ressourceout,timeout))
		else :
			(done,notdone,gaveup,ressourceout,timeout)=zipper(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
			list_or_dict_to_json(done,sys.argv[2])
			print(zipper_stat(done,notdone,gaveup,ressourceout,timeout))
