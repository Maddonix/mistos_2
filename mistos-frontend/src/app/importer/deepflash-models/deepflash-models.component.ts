import { Component, OnInit } from '@angular/core';
import { ComService } from 'src/app/shared/com.service';

@Component({
  selector: 'app-deepflash-models',
  templateUrl: './deepflash-models.component.html',
  styleUrls: ['./deepflash-models.component.css']
})
export class DeepflashModelsComponent implements OnInit {
  title = 'dropzone';
  deepflashModels: File[] = [];
  modelInputPath = "";
  messageDeepflash:string="";
  meassageFilePathRead:string="";
  uploadResponse: string;//any = { status: '', message: ''};
  error:string;
  uploadModes = [
    "image",
    "max-z-projection",
    "tilescan"
  ];
  uploadMode:string="image";
  constructor(private comService: ComService) { }

  ngOnInit(): void {
  }

  uploadDeepflashModels(idx, file) {
    this.comService.uploadDeepflashModels(file).subscribe(
      (res) => {
        this.uploadResponse = "File "+ idx.toString() + JSON.stringify(res);
      },
      (err) => {this.error = err;}
    )
  }

  onUploadDeepflashModelsClicked() {
    console.log(this.deepflashModels);
    this.messageDeepflash = "";
  
    for (let i = 0; i < this.deepflashModels.length; i++) {
      this.uploadDeepflashModels(i, this.deepflashModels[i]);
    }
  };
  
  onDeepflashModelAdded(event) {
      console.log(event);
      this.deepflashModels.push(...event.addedFiles);
      const formData = new FormData();
      for (var i = 0; i < this.deepflashModels.length; i++) { 
        formData.append("file[]", this.deepflashModels[i]);
      }
  };
  
  onRemoveDeepflashModel(event) {
      console.log(event);
      this.deepflashModels.splice(this.deepflashModels.indexOf(event), 1);
  };

  onUploadDeepflashModelFromFilepath() {
    this.comService.uploadDfModelFromFilepath(this.modelInputPath).subscribe((res)=>{
      this.meassageFilePathRead = JSON.stringify(res);
    });
  }

}
