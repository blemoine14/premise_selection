from predictionManager import *
from zipper_utils import *
import itertools
from shutil import copyfile
import argparse

def tactic_seuil(predictionManager,zf_dir_path,list_of_lemme,k=1,k_max=None) :

    if max_k is None :
    	max_k=len(predictionManager.reseau.binarizer.classes_)
    
    if list_of_lemme is None :
        list_of_lemme = predictionManager.dataManager.th_names
    
    if not(list_of_lemme and k < k_max) : #possède au moins un élément
        return []
    
    global zipper_exec_time
    print("size_of_echantillon =",len(list_of_lemme))
    print("starting")
    
    print("create files")

    copyfile(pm.dataManager.data_dir+pm.dataManager.rew_type_file, zf_dir_path+pm.dataManager.rew_type_file)

    for chapter in predictionManager.dataManager.struct_dict :
        for lemme in predictionManager.dataManager.struct_dict[chapter] :
            if lemme in list_of_lemme :
	            zf_file=zf_dir_path+predictionManager.dataManager.get_chapter(lemme)+"/"+lemme+".zf"
	            predictionManager.th_name_pred_top_k_to_zf_file(lemme,zf_file,k=k)
                
    print("file created")
                
    threads=[]

    for chapter in predictionManager.dataManager.struct_dict :

        zipper_exec_time[chapter]=dict()

        for lemme in predictionManager.dataManager.struct_dict[chapter] :
            if lemme in list_of_lemme :
                threads.append(Zipperposition(zf_dir_path,chapter,lemme))

    for i in range(len(threads)):
        with semZ :
            threads[i].start()

    for i in range(len(threads)):
        threads[i].join()
    
    done,notdone,gaveup,ressourceout,timeout = get_zipper_stat(zipper_exec_time)
    
    print("Seuil done : "+str(seuil))
    print(zipper_stat(done,notdone,gaveup,ressourceout,timeout))

    data_list = tactic_seuil(predictionManager,zf_dir_path,notdone,k+k//10+1,max_k)
    return [[seuil,done,notdone,gaveup,ressourceout,timeout]]+data_list


def display_data(datas) :
    seuil=[]
    done=[]
    notdone=[]
    gaveup=[]
    ressourceout=[]
    timeout=[]
    for i in range(len(datas)) :
        seuil.append(datas[i][0])
        done.append(len(list(itertools.chain.from_iterable([data[1] for data in datas[:(i+1)]]))))
        notdone.append(len(datas[i][2]))
        gaveup.append(len(datas[i][3]))
        ressourceout.append(len(datas[i][4]))
        timeout.append(len(datas[i][5]))
    x=seuil
    y1=done
    y2=notdone
    y3=gaveup
    y4=ressourceout
    y5=timeout
    plt.plot(x,y1,linewidth=2.0,label = "done")
    plt.xlim(x[0]+0.01,x[-1]-0.01)
    plt.legend()
    plt.show()
    print(done[len(done)-1],"/",(done[len(done)-1]+notdone[len(notdone)-1]))
    print(datas[len(datas)-1][2])
    return list(itertools.chain.from_iterable([data[1] for data in datas[:(i+1)]]))


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("network_save", help="dossier contenant la sauvegarde du reseau a utiliser")
	parser.add_argument("zf_dir", help="dossier de destination des fichiers .zf generes")
	parser.add_argument("save_data_file", help="fichier de sauvegarde des donnees de la tactique")
	parser.add_argument("-ki","--k_init",default=0, help="nombre de premisses selectionnees pour la premiere iteration", type=int)
	parser.add_argument("-km","--k_max", help="nombre maximal de premisses selectionnees pour la derniere iteration (par defaut = nombre de premisses connues par le reseau, type=int)", type=int)
	args = parser.parse_args()
	

	dm=DataManager(data_dir="../datas/",rew_def_file="rew_def.zf",ax_th_def_file="ax_th_def.zf",struct_file="config_struct.json",rew_type_list="rew_type.json",rew_type_file="rew_type.zf")
	res=Reseau()
	res.load(args.network_save)
	pm=PredictionManager(dm,res)
	k_max=None
	if args.k_max :
		k_max=args.k_max
	datas=tactic_seuil(pm,args.zf_dir,None,k=args.k_init,k_max=k_max)
	with open(args.save_data_file, "wb") as fp:
			pickle.dump(datas, fp)
	done=display_data(datas)
