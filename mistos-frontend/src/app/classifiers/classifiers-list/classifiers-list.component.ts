import { AfterViewInit, Component, OnInit, ViewChild } from '@angular/core';
import { MatDialog, MatDialogConfig } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { ActivatedRoute, Data, Router } from '@angular/router';
import { MatTableFilter } from 'mat-table-filter';
import { Subscription } from 'rxjs';
import { WarningDeleteComponent } from 'src/app/dialogs/warning-delete/warning-delete.component';
import { Classifier } from 'src/app/models/classifier.model';
import { ClassifierService } from 'src/app/shared/classifier.service';
import { ComService } from 'src/app/shared/com.service';

@Component({
  selector: 'app-classifiers-list',
  templateUrl: './classifiers-list.component.html',
  styleUrls: ['./classifiers-list.component.css']
})
export class ClassifiersListComponent implements AfterViewInit, OnInit {
  @ViewChild(MatSort) sort: MatSort;
  @ViewChild(MatPaginator) paginator: MatPaginator;

  filterEntity: Classifier;
  filterType: MatTableFilter;
  dataSource: MatTableDataSource<Classifier>;//ImagesListDataSource;
  classifierList: Classifier[];
  subscription: Subscription;
  displayedColumns = ['uid', 'name', "clfType", "tags", "actions"];
  dialogConfig = new MatDialogConfig();

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private dialog: MatDialog,
    private comService:ComService
  ) { }

  ngOnInit(): void {
    this.route.data.subscribe((data:Data) => {
      this.classifierList = data["classifierList"];
          //Setup Dialog Config File
    this.dialogConfig.disableClose = true; //disables closing by clicking outside of the dialog
    this.dialogConfig.autoFocus = true; //focus will automatically set on the first form field
    this.dialogConfig.hasBackdrop = true; //prevents user from clicking on the rest of the ui
    this.dialogConfig.closeOnNavigation = true; //closes dialog if wen navigate to another route
    });

    // Components for filtering
    this.filterEntity = new Classifier();
    this.filterType = MatTableFilter.ANYWHERE;
    //create dataSource for table
    this.dataSource = new MatTableDataSource(this.classifierList);
  }

  ngAfterViewInit() {
    // Here we define sorting, pagination and our datasource
    this.dataSource = new MatTableDataSource(this.classifierList);
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }

  onSelect(classifierId: number) {
    this.router.navigate([classifierId, "hint"], {relativeTo: this.route});
  }

  onFetchData() {
    this.dataSource = new MatTableDataSource(this.classifierList);
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }

  onDelete(classifierId:number) {
    this.dialogConfig.data = {
      warningInput: "this classifier"
    };

    const dialogRef = this.dialog.open(         //dialogRef is a observable of the dialog
      WarningDeleteComponent,
      this.dialogConfig
    );
    dialogRef.afterClosed().subscribe((proceed:boolean)=> {
      if (proceed === true) {
        this.comService.deleteClassifierById(classifierId).subscribe((response) => {
          console.log("DeleteClassifierRequest:");
          console.log(response);
          
          this.comService.fetchClassifierList().subscribe((imageList:Classifier[]) => {
            this.classifierList = imageList;
            this.onFetchData();
          });
      });
      } else {
        console.log("Delete Classifier was aboirted.");
      }
    }
    ) 
  }

}
