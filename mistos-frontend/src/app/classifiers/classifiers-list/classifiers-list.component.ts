import { AfterViewInit, Component, OnInit, ViewChild } from '@angular/core';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { ActivatedRoute, Data, Router } from '@angular/router';
import { MatTableFilter } from 'mat-table-filter';
import { Subscription } from 'rxjs';
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

  constructor(
    private comService: ComService,
    private classifierService: ClassifierService,
    private router: Router,
    private route: ActivatedRoute
  ) { }

  ngOnInit(): void {
    // Subscribe to Classifier List
    // this.subscription = this.classifierService.classifierListChanged.subscribe((classifierList:Classifier[]) => {
    //   this.classifierList = classifierList;
    // });
    // this.classifierList = this.classifierService.getClassifierList();
    this.route.data.subscribe((data:Data) => {
      this.classifierList = data["classifierList"];
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

}
