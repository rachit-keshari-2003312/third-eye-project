import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'conversations',
    pathMatch: 'full'
  },
  {
    path: 'conversations',
    loadComponent: () => import('./pages/conversations/conversations.component').then(m => m.ConversationsComponent)
  },
  {
    path: 'analytics',
    loadComponent: () => import('./pages/analytics/analytics.component').then(m => m.AnalyticsComponent)
  },
  {
    path: '**',
    redirectTo: 'conversations'
  }
];